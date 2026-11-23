"""
Sync cursor + execution lease state (DQV cursor_state.py — async port).

Mirrors cognitedata/data-quality-validation:
  cognite_data_quality/_function_code/common/cursor_state.py
"""

from __future__ import annotations

import time

from cognite.client import AsyncCogniteClient
from cognite.client.data_classes.data_modeling import NodeApply, ViewId
from cognite.client.data_classes.data_modeling.ids import ContainerId, NodeId
from cognite.client.data_classes.data_modeling.instances import NodeOrEdgeData

from models import SyncCursorState, SyncLockNodeState


def instance_space_key_from_list(instance_spaces: list[str]) -> str:
    return "+".join(sorted(instance_spaces))


def sync_cursor_external_id(
    view_space: str, view_external_id: str, instance_space_key: str
) -> str:
    return f"sync_cursor_{view_space}_{view_external_id}_{instance_space_key}"


def sync_lock_external_id(
    view_space: str, view_external_id: str, instance_space_key: str
) -> str:
    return f"sync_lock_{view_space}_{view_external_id}_{instance_space_key}"


def _state_view_id(platform_space: str, view_version: str) -> ViewId:
    return ViewId(platform_space, "FunctionSyncState", view_version)


def _state_container_id(platform_space: str) -> ContainerId:
    return ContainerId(platform_space, "FunctionSyncState")


def _view_properties(node: object, view_id: ViewId) -> dict[str, object]:
    props_map = getattr(node, "properties", None) or {}
    if view_id in props_map:
        return dict(props_map[view_id])
    for key, val in props_map.items():
        if getattr(key, "external_id", None) == view_id.external_id:
            return dict(val)
    if "syncCursor" in props_map or "orchestration_id" in props_map:
        return dict(props_map)
    return {}


async def load_sync_cursor(
    client: AsyncCogniteClient,
    view_space: str,
    view_external_id: str,
    instance_space_key: str,
    platform_space: str,
    platform_view_version: str,
) -> SyncCursorState | None:
    external_id = sync_cursor_external_id(view_space, view_external_id, instance_space_key)
    view_id = _state_view_id(platform_space, platform_view_version)
    nodes = await client.data_modeling.instances.retrieve_nodes(
        [NodeId(platform_space, external_id)],
        sources=[view_id],
    )
    if not nodes:
        return None
    node = nodes[0]
    props = _view_properties(node, view_id)
    cursor = props.get("syncCursor")
    if cursor:
        stored_oid = props.get("orchestration_id")
        job_run_id = stored_oid if isinstance(stored_oid, str) and stored_oid else None
        return SyncCursorState(
            cursor=str(cursor),
            processed_count=int(props.get("processedCount") or 0),
            job_run_id=job_run_id,
            version=node.version,
        )
    return SyncCursorState(version=node.version) if node.version is not None else None


async def save_sync_cursor(
    client: AsyncCogniteClient,
    view_space: str,
    view_external_id: str,
    instance_space_key: str,
    cursor: str,
    processed_count: int,
    job_run_id: str,
    platform_space: str,
    platform_view_version: str,
    existing_version: int | None = None,
) -> int | None:
    external_id = sync_cursor_external_id(view_space, view_external_id, instance_space_key)
    node = NodeApply(
        space=platform_space,
        external_id=external_id,
        existing_version=existing_version,
        sources=[
            NodeOrEdgeData(
                source=_state_container_id(platform_space),
                properties={
                    "orchestration_id": job_run_id,
                    "partitionId": "sync",
                    "syncCursor": cursor,
                    "processedCount": processed_count,
                    "lastUpdated": int(time.time() * 1000),
                },
            )
        ],
    )
    result = await client.data_modeling.instances.apply(
        [node], skip_on_version_conflict=True
    )
    nodes = getattr(result, "nodes", None) or []
    if existing_version is not None and not nodes:
        return None
    return nodes[0].version if nodes else existing_version


async def _load_sync_lock_node(
    client: AsyncCogniteClient,
    view_space: str,
    view_external_id: str,
    instance_space_key: str,
    platform_space: str,
    platform_view_version: str,
) -> tuple[SyncLockNodeState | None, int | None]:
    external_id = sync_lock_external_id(view_space, view_external_id, instance_space_key)
    view_id = _state_view_id(platform_space, platform_view_version)
    nodes = await client.data_modeling.instances.retrieve_nodes(
        [NodeId(platform_space, external_id)],
        sources=[view_id],
    )
    if not nodes or not nodes[0].properties:
        return None, None
    return (
        SyncLockNodeState.from_node_properties(_view_properties(nodes[0], view_id)),
        nodes[0].version,
    )


async def initialize_sync_lock_node(
    client: AsyncCogniteClient,
    view_space: str,
    view_external_id: str,
    instance_space_key: str,
    platform_space: str,
    platform_view_version: str,
) -> None:
    try:
        existing_state, _ = await _load_sync_lock_node(
            client,
            view_space,
            view_external_id,
            instance_space_key,
            platform_space,
            platform_view_version,
        )
    except Exception:
        return
    if existing_state is not None:
        return

    external_id = sync_lock_external_id(view_space, view_external_id, instance_space_key)
    node = NodeApply(
        space=platform_space,
        external_id=external_id,
        sources=[
            NodeOrEdgeData(
                source=_state_container_id(platform_space),
                properties={
                    "orchestration_id": "",
                    "partitionId": "lock",
                    "syncCursor": "",
                    "processedCount": 0,
                    "lastUpdated": 0,
                },
            )
        ],
    )
    await client.data_modeling.instances.apply([node])


async def try_acquire_sync_lock(
    client: AsyncCogniteClient,
    view_space: str,
    view_external_id: str,
    instance_space_key: str,
    holder_id: str,
    ttl_ms: int,
    platform_space: str,
    platform_view_version: str,
    *,
    known_version: int | None = None,
) -> tuple[bool, int | None]:
    now_ms = int(time.time() * 1000)
    expires_ms = now_ms + ttl_ms
    external_id = sync_lock_external_id(view_space, view_external_id, instance_space_key)

    try:
        lock_state, version = await _load_sync_lock_node(
            client,
            view_space,
            view_external_id,
            instance_space_key,
            platform_space,
            platform_view_version,
        )
    except Exception:
        return False, None

    if lock_state is None:
        await initialize_sync_lock_node(
            client,
            view_space,
            view_external_id,
            instance_space_key,
            platform_space,
            platform_view_version,
        )
        try:
            lock_state, version = await _load_sync_lock_node(
                client,
                view_space,
                view_external_id,
                instance_space_key,
                platform_space,
                platform_view_version,
            )
        except Exception:
            return False, None

    if known_version is not None and version != known_version:
        return False, None

    if lock_state and lock_state.orchestration_id and lock_state.orchestration_id != holder_id:
        if lock_state.last_updated > now_ms:
            return False, None

    node = NodeApply(
        space=platform_space,
        external_id=external_id,
        existing_version=version,
        sources=[
            NodeOrEdgeData(
                source=_state_container_id(platform_space),
                properties={
                    "orchestration_id": holder_id,
                    "partitionId": "lock",
                    "syncCursor": "",
                    "processedCount": 0,
                    "lastUpdated": expires_ms,
                },
            )
        ],
    )
    result = await client.data_modeling.instances.apply(
        [node], skip_on_version_conflict=True
    )
    nodes = getattr(result, "nodes", None) or []
    if version is not None and not nodes:
        return False, None
    new_version = nodes[0].version if nodes else version
    return True, new_version


async def refresh_sync_lock(
    client: AsyncCogniteClient,
    view_space: str,
    view_external_id: str,
    instance_space_key: str,
    holder_id: str,
    ttl_ms: int,
    platform_space: str,
    platform_view_version: str,
    *,
    known_version: int | None,
) -> tuple[bool, int | None]:
    if known_version is None:
        return False, None
    try:
        lock_state, loaded_version = await _load_sync_lock_node(
            client,
            view_space,
            view_external_id,
            instance_space_key,
            platform_space,
            platform_view_version,
        )
    except Exception:
        return False, None
    if not lock_state or loaded_version != known_version:
        return False, None
    if lock_state.orchestration_id != holder_id:
        return False, None
    return await try_acquire_sync_lock(
        client,
        view_space,
        view_external_id,
        instance_space_key,
        holder_id,
        ttl_ms,
        platform_space,
        platform_view_version,
        known_version=known_version,
    )


async def release_sync_lock(
    client: AsyncCogniteClient,
    view_space: str,
    view_external_id: str,
    instance_space_key: str,
    holder_id: str,
    platform_space: str,
    platform_view_version: str,
    *,
    known_version: int | None = None,
) -> None:
    try:
        lock_state, version = await _load_sync_lock_node(
            client,
            view_space,
            view_external_id,
            instance_space_key,
            platform_space,
            platform_view_version,
        )
    except Exception:
        return
    if known_version is not None:
        version = known_version
    if not lock_state or lock_state.orchestration_id != holder_id:
        return

    external_id = sync_lock_external_id(view_space, view_external_id, instance_space_key)
    node = NodeApply(
        space=platform_space,
        external_id=external_id,
        existing_version=version,
        sources=[
            NodeOrEdgeData(
                source=_state_container_id(platform_space),
                properties={
                    "orchestration_id": "",
                    "partitionId": "lock",
                    "syncCursor": "",
                    "processedCount": 0,
                    "lastUpdated": 0,
                },
            )
        ],
    )
    await client.data_modeling.instances.apply([node], skip_on_version_conflict=True)
