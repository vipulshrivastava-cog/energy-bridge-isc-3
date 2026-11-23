"""Unit tests for hierarchy path/cycle logic (no CDF client)."""

from common.hierarchy_logic import (
    collect_descendant_ids,
    compute_path_chain,
    would_create_cycle,
)
from common.path_materializer import node_needs_path_recompute

# TC-006 baseline BusinessUnits parent map (bu_apac under bh_root)
TC006_BASELINE_PARENTS: dict[str, str | None] = {
    "bh_root": None,
    "bu_emea": "bh_root",
    "bu_apac": "bh_root",
    "cc_1100": "bu_emea",
    "cc_1110": "cc_1100",
    "cc_1120": "cc_1110",
    "cc_1200": "bu_emea",
    "cc_1210": "cc_1200",
    "cc_1220": "cc_1200",
    "cc_2100": "bu_apac",
    "cc_2110": "cc_2100",
}

# TC-006 after step 2: bu_apac reparented under bh_corp_apac
TC006_REPARENT_PARENTS: dict[str, str | None] = {
    **TC006_BASELINE_PARENTS,
    "bh_corp_apac": None,
    "bu_apac": "bh_corp_apac",
}


def test_root_self_reference_path() -> None:
    parents = {"bh_root": None}
    chain = compute_path_chain("bh_root", parents)
    assert chain.root_id == "bh_root"
    assert chain.path_ids == ["bh_root"]


def test_path_index_semantics_on_leaf() -> None:
    parents = {
        "bh_root": None,
        "bu_emea": "bh_root",
        "cc_1100": "bu_emea",
        "cc_1110": "cc_1100",
    }
    chain = compute_path_chain("cc_1110", parents)
    assert chain.root_id == "bh_root"
    assert chain.path_ids == ["bh_root", "bu_emea", "cc_1100", "cc_1110"]
    assert chain.path_ids[0] == "bh_root"
    assert chain.path_ids[-2] == "cc_1100"
    assert chain.path_ids[-1] == "cc_1110"


def test_cycle_detection() -> None:
    known = {"a": "b", "b": "c"}
    assert would_create_cycle("c", "a", known) is True
    assert would_create_cycle("d", "c", known) is False
    assert would_create_cycle("x", "x", known) is True


def test_tc006_subtree_descendants_after_reparent() -> None:
    """path_sync_cursor must expand bu_apac reparent to cc_2100 and cc_2110."""
    descendants = collect_descendant_ids({"bu_apac"}, TC006_REPARENT_PARENTS)
    assert descendants == {"cc_2100", "cc_2110"}


def test_tc006_paths_after_reparent_via_trigger_chain() -> None:
    """Expected root/path after dataModeling trigger → workflow → function."""
    targets = {"bu_apac", "cc_2100", "cc_2110"}
    descendants = collect_descendant_ids({"bu_apac"}, TC006_REPARENT_PARENTS)
    assert targets == {"bu_apac"} | descendants

    expected = {
        "bh_corp_apac": (["bh_corp_apac"], "bh_corp_apac"),
        "bu_apac": (["bh_corp_apac", "bu_apac"], "bh_corp_apac"),
        "cc_2100": (["bh_corp_apac", "bu_apac", "cc_2100"], "bh_corp_apac"),
        "cc_2110": (
            ["bh_corp_apac", "bu_apac", "cc_2100", "cc_2110"],
            "bh_corp_apac",
        ),
    }
    for node_id, (path_ids, root_id) in expected.items():
        chain = compute_path_chain(node_id, TC006_REPARENT_PARENTS)
        assert chain.path_ids == path_ids, node_id
        assert chain.root_id == root_id, node_id


def test_path_echo_does_not_need_recompute() -> None:
    """Own path writes re-trigger the workflow; stale filter must skip them."""
    props = {
        "name": "APAC Sourcing",
        "root": {"externalId": "bh_corp_apac"},
        "path": [
            {"externalId": "bh_corp_apac"},
            {"externalId": "bu_apac"},
        ],
    }
    assert (
        node_needs_path_recompute("bu_apac", TC006_REPARENT_PARENTS, props) is False
    )


def test_missing_path_still_needs_recompute() -> None:
    props = {"name": "APAC Sourcing", "parent": "bh_corp_apac"}
    existing = set(TC006_REPARENT_PARENTS.keys())
    assert (
        node_needs_path_recompute(
            "bu_apac", TC006_REPARENT_PARENTS, props, existing
        )
        is True
    )


# TC-004: ph_root deleted — dangling parent refs, orphan promotion (Option A)
TC004_AFTER_DELETE_PARENTS: dict[str, str | None] = {
    "ph_family_packaging": "ph_root",
    "ph_family_industrial": "ph_root",
    "ph_family_raw": "ph_root",
    "ph_group_cartons": "ph_family_packaging",
    "ph_group_labels": "ph_family_packaging",
    "ph_subgroup_folding": "ph_group_cartons",
    "ph_subgroup_corrugated": "ph_group_cartons",
    "ph_group_pallets": "ph_family_industrial",
    "ph_group_pulp": "ph_family_raw",
}
TC004_EXISTING_IDS = set(TC004_AFTER_DELETE_PARENTS.keys())


def test_tc004_orphan_promotion_new_roots() -> None:
    """Direct children of deleted ph_root become self-rooted."""
    for node_id in ("ph_family_packaging", "ph_family_industrial", "ph_family_raw"):
        chain = compute_path_chain(
            node_id, TC004_AFTER_DELETE_PARENTS, TC004_EXISTING_IDS
        )
        assert chain.root_id == node_id, node_id
        assert chain.path_ids == [node_id], node_id


def test_tc004_orphan_promotion_subtree_paths() -> None:
    """Descendants re-root under promoted forest roots (packaging subtree)."""
    expected = {
        "ph_subgroup_folding": (
            ["ph_family_packaging", "ph_group_cartons", "ph_subgroup_folding"],
            "ph_family_packaging",
        ),
        "ph_group_labels": (
            ["ph_family_packaging", "ph_group_labels"],
            "ph_family_packaging",
        ),
        "ph_group_pulp": (
            ["ph_family_raw", "ph_group_pulp"],
            "ph_family_raw",
        ),
    }
    for node_id, (path_ids, root_id) in expected.items():
        chain = compute_path_chain(
            node_id, TC004_AFTER_DELETE_PARENTS, TC004_EXISTING_IDS
        )
        assert chain.path_ids == path_ids, node_id
        assert chain.root_id == root_id, node_id


def test_tc004_stale_root_triggers_recompute() -> None:
    props = {
        "name": "Consumer Packaging",
        "root": {"externalId": "ph_root"},
        "path": [{"externalId": "ph_root"}, {"externalId": "ph_family_packaging"}],
    }
    assert (
        node_needs_path_recompute(
            "ph_family_packaging",
            TC004_AFTER_DELETE_PARENTS,
            props,
            TC004_EXISTING_IDS,
        )
        is True
    )


def test_tc004_path_without_root_needs_recompute() -> None:
    """CDF may null parent and leave path partially materialized without root."""
    props = {
        "name": "Consumer Packaging",
        "parent": None,
        "path": [{"externalId": "ph_family_packaging"}],
    }
    assert (
        node_needs_path_recompute(
            "ph_family_packaging",
            {"ph_family_packaging": None},
            props,
            {"ph_family_packaging"},
        )
        is True
    )
