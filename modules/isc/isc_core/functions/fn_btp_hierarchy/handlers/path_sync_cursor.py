"""path_sync_cursor — instances.sync + cursor → upsert root/path (DQV instance_sync_cursor)."""

from __future__ import annotations

import asyncio
import json
import time
from typing import Any

from cognite.client import AsyncCogniteClient, CogniteClient
from cognite.client.data_classes.data_modeling.query import (
    NodeResultSetExpressionSync,
    QuerySync,
    SelectSync,
    SourceSelector,
)
from cognite.client.data_classes.filters import And, HasData, In

from common.client import resolve_async_client
from common.cursor_state import load_sync_cursor, save_sync_cursor
from common.path_materializer import (
    dangling_parent_ids,
    filter_stale_path_roots,
    find_descendants,
    find_orphans_of_missing_parents,
    load_parent_map,
    recompute_paths,
)
from common.sync_lock import SyncLockSession
from models import HierarchyTaskInput, PathSyncResult, SkippedResult

SYNC_BASE_LIMITS = [1000, 500, 200, 100, 10]


def _log_event(event: str, task: HierarchyTaskInput, **fields: object) -> None:
    """Structured log line — visible in CDF function call logs (stdout)."""
    payload = {
        "event": event,
        "handler": "path_sync_cursor",
        "view": task.view_label(),
        **fields,
    }
    print(json.dumps(payload, default=str))


async def _run_path_sync_cursor(
    client: AsyncCogniteClient,
    task: HierarchyTaskInput,
) -> dict[str, object]:
    lock = SyncLockSession(client, task, task.sync_lock)
    if not await lock.acquire():
        _log_event("skipped", task, reason="concurrent_execution")
        return SkippedResult(mode="path_sync_cursor").to_response()

    start_time = time.time()
    chunk_num = 0
    total_upserted = 0
    echo_chunks_skipped = 0
    cursor_state = await load_sync_cursor(
        client,
        task.view_space,
        task.view_external_id,
        task.instance_space_key,
        task.platform_space,
        task.platform_view_version,
    )
    current_cursor = cursor_state.cursor if cursor_state else None
    total_processed = cursor_state.processed_count if cursor_state else 0
    cursor_version = cursor_state.version if cursor_state else None
    job_run_id = (
        cursor_state.job_run_id if cursor_state and cursor_state.job_run_id else None
    ) or f"job_{int(time.time())}"

    _log_event(
        "start",
        task,
        job_run_id=job_run_id,
        max_runtime_seconds=task.max_runtime_seconds,
        chunk_size=task.chunk_size,
    )

    dms_filter = And(
        HasData(views=[task.view_id]),
        In(["node", "space"], task.instance_spaces),
    )

    sync_limits = [task.chunk_size] + [v for v in SYNC_BASE_LIMITS if v < task.chunk_size]
    sync_limit_idx = 0

    def _partial(reason: str, *, cursor_saved: bool | None = None) -> dict[str, object]:
        return PathSyncResult(
            status="partial",
            reason=reason,
            upserted_nodes=total_upserted,
            processed_count=total_processed + total_upserted,
            cursor_saved=cursor_saved if cursor_saved is not None else bool(current_cursor),
            elapsed_seconds=time.time() - start_time,
            view=task.view_label(),
        ).to_response()

    async def _save_cursor_safe(cursor_val: str, processed: int) -> bool:
        nonlocal cursor_version
        new_version = await save_sync_cursor(
            client,
            task.view_space,
            task.view_external_id,
            task.instance_space_key,
            cursor_val,
            processed,
            job_run_id,
            task.platform_space,
            task.platform_view_version,
            existing_version=cursor_version,
        )
        if new_version is not None:
            cursor_version = new_version
            return True
        return False

    cursor_before_chunk: str | None = current_cursor

    try:
        while True:
            if not await lock.heartbeat():
                return _partial("sync_lock_lost")
            elapsed = time.time() - start_time
            if elapsed > task.max_runtime_seconds:
                if current_cursor:
                    if not await _save_cursor_safe(current_cursor, total_processed + total_upserted):
                        return _partial("cursor_version_conflict", cursor_saved=False)
                _log_event(
                    "timeout",
                    task,
                    chunks_processed=chunk_num,
                    upserted_nodes=total_upserted,
                    echo_chunks_skipped=echo_chunks_skipped,
                    elapsed_seconds=round(elapsed, 2),
                )
                return _partial("timeout")

            cursor_before_chunk = current_cursor
            chunk_num += 1
            retries_at_limit = 0

            while True:
                sync_limit = sync_limits[sync_limit_idx]
                try:
                    query = QuerySync(
                        with_={
                            "nodes": NodeResultSetExpressionSync(
                                filter=dms_filter,
                                limit=sync_limit,
                                sync_mode="two_phase",
                            )
                        },
                        select={
                            "nodes": SelectSync(
                                sources=[
                                    SourceSelector(source=task.view_id, properties=["parent"])
                                ]
                            )
                        },
                        cursors={"nodes": current_cursor} if current_cursor else None,
                        allow_expired_cursors_and_accept_missed_deletes=True,
                    )
                    sync_result = await client.data_modeling.instances.sync(query)
                    break
                except Exception as exc:
                    error_msg = str(exc).lower()
                    if "timeout" in error_msg or "timed out" in error_msg:
                        retries_at_limit += 1
                        if retries_at_limit < 2:
                            await asyncio.sleep(30)
                        else:
                            retries_at_limit = 0
                            sync_limit_idx += 1
                            if sync_limit_idx >= len(sync_limits):
                                if current_cursor:
                                    await _save_cursor_safe(
                                        current_cursor, total_processed + total_upserted
                                    )
                                return PathSyncResult(
                                    status="partial",
                                    reason="sync_limits_exhausted",
                                    upserted_nodes=total_upserted,
                                    elapsed_seconds=time.time() - start_time,
                                    view=task.view_label(),
                                ).to_response()
                            await asyncio.sleep(30)
                    else:
                        raise

            changed_nodes = sync_result.get_nodes("nodes")
            deleted_ids = {
                node.external_id
                for node in changed_nodes
                if getattr(node, "deleted_time", None) is not None
            }
            live_changed_ids = {
                node.external_id
                for node in changed_nodes
                if getattr(node, "deleted_time", None) is None
            }
            new_cursor = (
                sync_result.cursors.get("nodes") if sync_result.cursors else None
            )
            has_more = new_cursor is not None and new_cursor != current_cursor
            current_cursor = new_cursor

            if not changed_nodes:
                if current_cursor:
                    await _save_cursor_safe(current_cursor, total_processed + total_upserted)
                break

            parent_by_id: dict[str, str | None] = {}
            props_by_id: dict[str, dict[str, object]] = {}
            existing_ids: set[str] = set()

            if live_changed_ids:
                parent_by_id, props_by_id, existing_ids = await load_parent_map(
                    client, task, live_changed_ids
                )

            missing_ancestor_ids = deleted_ids | dangling_parent_ids(
                parent_by_id, existing_ids
            )
            orphan_entry_ids: set[str] = set()
            if missing_ancestor_ids:
                orphan_entry_ids = await find_orphans_of_missing_parents(
                    client, task, missing_ancestor_ids
                )
                if orphan_entry_ids:
                    orphan_parent, orphan_props, orphan_existing = await load_parent_map(
                        client, task, orphan_entry_ids
                    )
                    parent_by_id.update(orphan_parent)
                    props_by_id.update(orphan_props)
                    existing_ids |= orphan_existing

            work_ids = live_changed_ids | orphan_entry_ids
            stale_roots = filter_stale_path_roots(
                work_ids, parent_by_id, props_by_id, existing_ids
            )

            if not stale_roots and not deleted_ids:
                echo_chunks_skipped += 1
                _log_event(
                    "path_echo_skip",
                    task,
                    chunk=chunk_num,
                    changed_nodes=len(live_changed_ids),
                    deleted_nodes=len(deleted_ids),
                    elapsed_seconds=round(time.time() - start_time, 2),
                )
                if current_cursor:
                    if not await _save_cursor_safe(
                        current_cursor, total_processed + total_upserted
                    ):
                        return _partial("cursor_version_conflict", cursor_saved=False)
                if not has_more:
                    break
                continue

            descendants = await find_descendants(client, task, stale_roots)
            target_ids = stale_roots | descendants
            updated = await recompute_paths(client, task, target_ids)
            total_upserted += updated
            _log_event(
                "chunk_done",
                task,
                chunk=chunk_num,
                stale_roots=len(stale_roots),
                descendants=len(descendants),
                deleted_ancestors=len(missing_ancestor_ids),
                orphan_entries=len(orphan_entry_ids),
                upserted=updated,
                elapsed_seconds=round(time.time() - start_time, 2),
            )

            if current_cursor:
                if not await _save_cursor_safe(
                    current_cursor, total_processed + total_upserted
                ):
                    return _partial("cursor_version_conflict", cursor_saved=False)

            if not has_more:
                break

        _log_event(
            "complete",
            task,
            status="completed",
            chunks_processed=chunk_num,
            upserted_nodes=total_upserted,
            echo_chunks_skipped=echo_chunks_skipped,
            elapsed_seconds=round(time.time() - start_time, 2),
        )
        return PathSyncResult(
            platform_space=task.platform_space,
            instance_spaces=task.instance_spaces,
            chunks_processed=chunk_num,
            upserted_nodes=total_upserted,
            echo_chunks_skipped=echo_chunks_skipped,
            processed_count=total_processed + total_upserted,
            cursor_saved=True,
            elapsed_seconds=time.time() - start_time,
            view=task.view_label(),
        ).to_response()
    except Exception:
        if cursor_before_chunk:
            await _save_cursor_safe(cursor_before_chunk, total_processed + total_upserted)
        raise
    finally:
        await lock.release()


def handle_path_sync_cursor(task: HierarchyTaskInput, client: CogniteClient | None) -> dict[str, Any]:
    async_client = resolve_async_client(client)
    return asyncio.run(_run_path_sync_cursor(async_client, task))
