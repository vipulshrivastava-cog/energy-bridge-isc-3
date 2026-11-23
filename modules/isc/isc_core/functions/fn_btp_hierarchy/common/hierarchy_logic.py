"""Pure hierarchy path/cycle logic (no CDF client dependencies)."""

from __future__ import annotations

from collections import defaultdict

from models import PathChain

MAX_PATH_DEPTH = 100


def would_create_cycle(
    external_id: str,
    parent_external_id: str | None,
    known_parents: dict[str, str | None],
) -> bool:
    if not parent_external_id or parent_external_id == external_id:
        return parent_external_id == external_id
    seen: set[str] = {external_id}
    current: str | None = parent_external_id
    while current:
        if current in seen:
            return True
        seen.add(current)
        current = known_parents.get(current)
    return False


def compute_path_chain(
    external_id: str,
    parent_by_id: dict[str, str | None],
    existing_ids: set[str] | None = None,
) -> PathChain:
    """Walk parent chain upward; stop at first live ancestor.

    When ``existing_ids`` is set, a parent reference to a missing/deleted node ends
    the walk at the current node (orphan promotion — TC-004).
    """
    chain: list[str] = []
    current: str | None = external_id
    seen: set[str] = set()
    while current and current not in seen:
        seen.add(current)
        chain.append(current)
        parent = parent_by_id.get(current)
        if parent and existing_ids is not None and parent not in existing_ids:
            break
        current = parent
    chain.reverse()
    if len(chain) > MAX_PATH_DEPTH:
        raise ValueError(f"path depth exceeds {MAX_PATH_DEPTH} for node {external_id}")
    return PathChain(root_id=chain[0], path_ids=chain)


def collect_descendant_ids(
    ancestor_ids: set[str],
    parent_by_id: dict[str, str | None],
) -> set[str]:
    """Return every descendant under ancestor_ids (full subtree, all levels).

    Mirrors `find_descendants` BFS — used by unit tests (TC-006, TC-009).
    """
    if not ancestor_ids:
        return set()

    children_by_parent: dict[str, set[str]] = defaultdict(set)
    for child_id, parent_id in parent_by_id.items():
        if parent_id:
            children_by_parent[parent_id].add(child_id)

    all_descendants: set[str] = set()
    frontier = set(ancestor_ids)

    for _ in range(MAX_PATH_DEPTH):
        children: set[str] = set()
        for parent_id in frontier:
            children |= children_by_parent.get(parent_id, set())
        new_children = children - ancestor_ids - all_descendants
        if not new_children:
            break
        all_descendants |= new_children
        frontier = new_children

    return all_descendants
