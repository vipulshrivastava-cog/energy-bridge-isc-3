"""raw_ingest_incremental — RAW cursor → upsert scalars + parent (DQV raw_validation)."""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from typing import Any

from cognite.client import AsyncCogniteClient, CogniteClient
from cognite.client.data_classes.data_modeling import NodeApply, ViewId
from cognite.client.data_classes.data_modeling.ids import ContainerId, NodeId
from cognite.client.data_classes.data_modeling.instances import NodeOrEdgeData

from common.cursor_state import _view_properties
from common.client import resolve_async_client
from common.hierarchy_logic import would_create_cycle
from common.sync_lock import SyncLockSession
from models import (
    DeferredIngestRow,
    HierarchyTaskInput,
    NodeReference,
    RawIngestResult,
    SkippedResult,
    coerce_scalar,
    derive_declared_type,
)

RAW_STATE_CONTAINER = "RawIngestState"


def _raw_state_view(platform_space: str, platform_view_version: str) -> ViewId:
    return ViewId(platform_space, RAW_STATE_CONTAINER, platform_view_version)


def _raw_state_node_id(db_name: str, table_name: str) -> str:
    safe_db = db_name.replace("-", "_")
    safe_table = table_name.replace("-", "_")
    return f"raw_ingest_{safe_db}_{safe_table}"


async def _load_raw_cursor(
    client: AsyncCogniteClient, task: HierarchyTaskInput, db_name: str, table_name: str
) -> int:
    node_id = NodeId(task.platform_space, _raw_state_node_id(db_name, table_name))
    nodes = await client.data_modeling.instances.retrieve_nodes(
        [node_id], sources=[_raw_state_view(task.platform_space, task.platform_view_version)]
    )
    if not nodes:
        return 0
    view_id = _raw_state_view(task.platform_space, task.platform_view_version)
    props = _view_properties(nodes[0], view_id)
    return int(props.get("last_processed_timestamp") or 0)


async def _save_raw_cursor(
    client: AsyncCogniteClient,
    task: HierarchyTaskInput,
    db_name: str,
    table_name: str,
    last_ts: int,
    rows_processed: int,
) -> None:
    node_external_id = _raw_state_node_id(db_name, table_name)
    properties = {
        "db_name": db_name,
        "table_name": table_name,
        "last_processed_timestamp": last_ts,
        "rows_processed": rows_processed,
        "last_run_time": datetime.now(timezone.utc),
    }
    apply = NodeApply(
        space=task.platform_space,
        external_id=node_external_id,
        sources=[
            NodeOrEdgeData(
                source=ContainerId(task.platform_space, RAW_STATE_CONTAINER),
                properties=properties,
            )
        ],
    )
    await client.data_modeling.instances.apply([apply])


async def _parent_exists(
    client: AsyncCogniteClient, task: HierarchyTaskInput, parent_external_id: str
) -> bool:
    nodes = await client.data_modeling.instances.retrieve_nodes(
        [NodeId(task.primary_instance_space, parent_external_id)],
        sources=[task.view_id],
    )
    return bool(nodes)


async def _run_raw_ingest_incremental(
    client: AsyncCogniteClient,
    task: HierarchyTaskInput,
) -> dict[str, object]:
    if not task.raw_db or not task.raw_table:
        raise ValueError("raw_db and raw_table required for raw_ingest_incremental")

    lock = SyncLockSession(client, task, task.sync_lock)
    if not await lock.acquire():
        return SkippedResult(mode="raw_ingest_incremental").to_response()

    try:
        last_ts = await _load_raw_cursor(client, task, task.raw_db, task.raw_table)
        mapping = task.merged_scalar_columns()
        applies: list[NodeApply] = []
        known_parents: dict[str, str | None] = {}
        deferred: list[DeferredIngestRow] = []
        max_ts = last_ts
        rows_seen = 0

        batch = await client.raw.rows.list(
            db_name=task.raw_db,
            table_name=task.raw_table,
            limit=task.batch_size,
            min_last_updated_time=last_ts + 1 if last_ts > 0 else None,
        )
        for row in batch:
            row_ts = int(getattr(row, "last_updated_time", None) or 0)
            if row_ts <= last_ts:
                continue
            max_ts = max(max_ts, row_ts)
            rows_seen += 1

            columns = row.columns if hasattr(row, "columns") else row
            raw_row_key = getattr(row, "key", None)
            external_id = coerce_scalar(columns.get("key") or raw_row_key, "name")
            if not external_id or not isinstance(external_id, str):
                continue

            properties: dict[str, object] = {}
            for raw_col, view_prop in mapping.items():
                raw_val = columns.get(raw_col)
                if raw_val is None:
                    continue
                coerced = coerce_scalar(raw_val, view_prop)
                if coerced is not None:
                    properties[view_prop] = coerced

            declared = derive_declared_type(properties)
            if declared:
                properties["declaredType"] = NodeId("sp_isc_organizational_foundation", declared)

            parent_raw = columns.get(task.parent_column)
            parent_eid = coerce_scalar(parent_raw, "name") if parent_raw else None
            parent_eid_str = str(parent_eid) if parent_eid else None
            deferred.append(
                DeferredIngestRow(
                    external_id=external_id,
                    properties=properties,
                    parent_external_id=parent_eid_str,
                )
            )

        still_deferred: list[DeferredIngestRow] = []
        cycles_rejected = 0
        pending = list(deferred)
        while pending:
            next_pending: list[DeferredIngestRow] = []
            wave_applies: list[NodeApply] = []
            for row in pending:
                if row.parent_external_id and not await _parent_exists(
                    client, task, row.parent_external_id
                ):
                    next_pending.append(row)
                    continue
                if would_create_cycle(row.external_id, row.parent_external_id, known_parents):
                    cycles_rejected += 1
                    continue
                known_parents[row.external_id] = row.parent_external_id
                properties = dict(row.properties)
                if row.parent_external_id:
                    properties["parent"] = NodeReference(
                        space=task.primary_instance_space,
                        external_id=row.parent_external_id,
                    ).to_wire()
                else:
                    properties["parent"] = None
                wave_applies.append(
                    NodeApply(
                        space=task.primary_instance_space,
                        external_id=row.external_id,
                        sources=[NodeOrEdgeData(source=task.view_id, properties=properties)],
                    )
                )
            if wave_applies:
                await client.data_modeling.instances.apply(wave_applies)
                applies.extend(wave_applies)
            if not wave_applies:
                still_deferred = next_pending
                break
            pending = next_pending
        else:
            still_deferred = []

        if max_ts > last_ts:
            await _save_raw_cursor(
                client, task, task.raw_db, task.raw_table, max_ts, len(applies)
            )

        return RawIngestResult(
            raw_db=task.raw_db,
            raw_table=task.raw_table,
            rows_scanned=rows_seen,
            upserted_nodes=len(applies),
            deferred_nodes=len(still_deferred),
            cycles_rejected=cycles_rejected,
            cursor_advanced_to=max_ts,
            view=task.view_label(),
        ).to_response()
    finally:
        await lock.release()


def handle_raw_ingest_incremental(
    task: HierarchyTaskInput, client: CogniteClient | None
) -> dict[str, Any]:
    async_client = resolve_async_client(client)
    return asyncio.run(_run_raw_ingest_incremental(async_client, task))
