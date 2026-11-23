"""Materialize root/path on hierarchy nodes from parent chain."""

from __future__ import annotations

from datetime import datetime, timezone

from cognite.client import AsyncCogniteClient
from cognite.client.data_classes.data_modeling import NodeApply
from cognite.client.data_classes.data_modeling.ids import NodeId
from cognite.client.data_classes.data_modeling.query import (
    NodeResultSetExpression,
    Query,
    Select,
    SourceSelector,
)
from cognite.client.data_classes.data_modeling.instances import NodeOrEdgeData
from cognite.client.data_classes.filters import And, Equals, HasData, In, Or

from common.hierarchy_logic import MAX_PATH_DEPTH, compute_path_chain
from models import HierarchyTaskInput, NodeReference, PathChain


def external_id_from_ref(value: object) -> str | None:
    if value is None:
        return None
    if isinstance(value, NodeId):
        return value.external_id
    if isinstance(value, dict):
        instance_id = value.get("instanceId") or value
        if isinstance(instance_id, dict):
            external_id = instance_id.get("externalId")
            return str(external_id) if external_id else None
    return None


def path_apply(
    task: HierarchyTaskInput,
    external_id: str,
    space: str,
    path_chain: PathChain,
    existing_props: dict[str, object] | None = None,
) -> NodeApply:
    now = datetime.now(timezone.utc)
    props = {
        k: v
        for k, v in (existing_props or {}).items()
        if k not in {"root", "path", "pathLastUpdatedTime", "children"}
    }
    props.update(
        {
            "root": NodeReference(space=space, external_id=path_chain.root_id).to_wire(),
            "path": [
                NodeReference(space=space, external_id=eid).to_wire()
                for eid in path_chain.path_ids
            ],
            "pathLastUpdatedTime": now,
        }
    )
    return NodeApply(
        space=space,
        external_id=external_id,
        sources=[NodeOrEdgeData(source=task.view_id, properties=props)],
    )


def _view_props(node: object, view_id: object) -> dict[str, object]:
    props_map = getattr(node, "properties", None) or {}
    if view_id in props_map:
        return dict(props_map[view_id])
    for key, val in props_map.items():
        if getattr(key, "external_id", None) == getattr(view_id, "external_id", None):
            return dict(val)
    return {}


async def load_parent_map(
    client: AsyncCogniteClient,
    task: HierarchyTaskInput,
    seed_ids: set[str],
) -> tuple[dict[str, str | None], dict[str, dict[str, object]], set[str]]:
    parent_by_id: dict[str, str | None] = {}
    props_by_id: dict[str, dict[str, object]] = {}
    to_fetch = set(seed_ids)

    while to_fetch:
        batch = list(to_fetch)[:100]
        to_fetch -= set(batch)
        nodes = await client.data_modeling.instances.retrieve_nodes(
            [NodeId(task.primary_instance_space, eid) for eid in batch],
            sources=[task.view_id],
        )
        for node in nodes:
            props = _view_props(node, task.view_id)
            props_by_id[node.external_id] = props
            parent_eid = external_id_from_ref(props.get("parent"))
            parent_by_id[node.external_id] = parent_eid
            if parent_eid and parent_eid not in parent_by_id:
                to_fetch.add(parent_eid)

    return parent_by_id, props_by_id, set(props_by_id.keys())


def dangling_parent_ids(
    parent_by_id: dict[str, str | None],
    existing_ids: set[str],
) -> set[str]:
    """Parent external IDs referenced on instances but not retrievable (deleted/missing)."""
    return {parent for parent in parent_by_id.values() if parent and parent not in existing_ids}


async def find_orphans_of_missing_parents(
    client: AsyncCogniteClient,
    task: HierarchyTaskInput,
    missing_parent_ids: set[str],
) -> set[str]:
    """Nodes affected when an ancestor was deleted or is missing.

    CDF hard-delete often **nulls** dangling ``parent`` refs, so a parent-pointer
    query alone misses orphan entry nodes (TC-004). Also scan stored ``root`` /
    ``path`` for references to deleted ids and repair partial writes (path without
    root).
    """
    if not missing_parent_ids:
        return set()

    affected = await _find_direct_children(client, task, missing_parent_ids)

    dms_filter = And(
        HasData(views=[task.view_id]),
        In(["node", "space"], task.instance_spaces),
    )
    nodes = await client.data_modeling.instances.list(
        instance_type="node",
        space=task.primary_instance_space,
        filter=dms_filter,
        sources=[task.view_id],
        limit=10_000,
    )
    for node in nodes:
        props = _view_props(node, task.view_id)
        if not props.get("name"):
            continue
        root_id = external_id_from_ref(props.get("root"))
        path_ids = _existing_path_ids(props) or []
        if root_id in missing_parent_ids or any(
            part in missing_parent_ids for part in path_ids
        ):
            affected.add(node.external_id)
        elif props.get("path") and not props.get("root"):
            affected.add(node.external_id)

    return affected


async def _find_direct_children(
    client: AsyncCogniteClient,
    task: HierarchyTaskInput,
    parent_ids: set[str],
) -> set[str]:
    """Return nodes whose parent points at any id in parent_ids."""
    if not parent_ids:
        return set()

    parent_property = [
        task.view_space,
        f"{task.view_external_id}/{task.view_version}",
        "parent",
    ]
    parent_filters = [
        Equals(
            parent_property,
            NodeReference(
                space=task.primary_instance_space,
                external_id=parent_id,
            ).to_wire(),
        )
        for parent_id in parent_ids
    ]
    desc_filter = parent_filters[0] if len(parent_filters) == 1 else Or(*parent_filters)

    query = Query(
        with_={"descendants": NodeResultSetExpression(filter=desc_filter)},
        select={
            "descendants": Select(
                sources=[SourceSelector(source=task.view_id, properties=["parent"])],
            )
        },
    )
    result = await client.data_modeling.instances.query(query)
    return {node.external_id for node in result.get_nodes("descendants")}


async def find_descendants(
    client: AsyncCogniteClient,
    task: HierarchyTaskInput,
    ancestor_ids: set[str],
) -> set[str]:
    """Return every descendant under ancestor_ids (full subtree, all levels).

    When an ancestor is reparented, path must be recomputed for the entire subtree
    in the same path_sync_cursor run — not only direct children (TC-006, TC-009).
    """
    if not ancestor_ids:
        return set()

    all_descendants: set[str] = set()
    frontier = set(ancestor_ids)

    for _ in range(MAX_PATH_DEPTH):
        children = await _find_direct_children(client, task, frontier)
        new_children = children - ancestor_ids - all_descendants
        if not new_children:
            break
        all_descendants |= new_children
        frontier = new_children

    return all_descendants


def node_needs_path_recompute(
    external_id: str,
    parent_by_id: dict[str, str | None],
    props: dict[str, object],
    existing_ids: set[str] | None = None,
) -> bool:
    """True when root/path are missing or inconsistent with the parent chain."""
    if not props.get("name"):
        return False
    if not props.get("path") or not props.get("root"):
        return True
    existing_root = external_id_from_ref(props.get("root"))
    existing_path = _existing_path_ids(props)
    if existing_root is None or existing_path is None:
        return True
    if existing_ids is None:
        existing_ids = set(parent_by_id.keys())
    expected = compute_path_chain(external_id, parent_by_id, existing_ids)
    return existing_root != expected.root_id or existing_path != expected.path_ids


def filter_stale_path_roots(
    candidate_ids: set[str],
    parent_by_id: dict[str, str | None],
    props_by_id: dict[str, dict[str, object]],
    existing_ids: set[str] | None = None,
) -> set[str]:
    """Return nodes that actually need path materialization (excludes path-write echoes)."""
    if existing_ids is None:
        existing_ids = set(props_by_id.keys())
    return {
        eid
        for eid in candidate_ids
        if node_needs_path_recompute(
            eid, parent_by_id, props_by_id.get(eid, {}), existing_ids
        )
    }


def _existing_path_ids(props: dict[str, object]) -> list[str] | None:
    path = props.get("path")
    if not path or not isinstance(path, list):
        return None
    ids: list[str] = []
    for part in path:
        eid = external_id_from_ref(part)
        if eid:
            ids.append(eid)
    return ids or None


async def recompute_paths(
    client: AsyncCogniteClient,
    task: HierarchyTaskInput,
    target_ids: set[str],
) -> int:
    if not target_ids:
        return 0

    parent_by_id, props_by_id, existing_ids = await load_parent_map(
        client, task, target_ids
    )
    missing_names = [eid for eid in target_ids if not props_by_id.get(eid, {}).get("name")]
    if missing_names:
        nodes = await client.data_modeling.instances.retrieve_nodes(
            [NodeId(task.primary_instance_space, eid) for eid in missing_names],
            sources=[task.view_id],
        )
        for node in nodes:
            props_by_id[node.external_id] = _view_props(node, task.view_id)
            existing_ids.add(node.external_id)

    applies = []
    for external_id in sorted(target_ids):
        existing = props_by_id.get(external_id, {})
        if not existing.get("name"):
            continue
        path_chain = compute_path_chain(external_id, parent_by_id, existing_ids)
        existing_root = external_id_from_ref(existing.get("root"))
        existing_path = _existing_path_ids(existing)
        if (
            existing_root is not None
            and existing_root == path_chain.root_id
            and existing_path == path_chain.path_ids
        ):
            continue
        applies.append(
            path_apply(
                task,
                external_id,
                task.primary_instance_space,
                path_chain,
                existing,
            )
        )

    if not applies:
        return 0

    await client.data_modeling.instances.apply(applies)
    return len(applies)
