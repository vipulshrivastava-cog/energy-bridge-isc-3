---
name: isc-sandbox
description: >-
  How to read supply chain data by writing Cognite Python SDK code in the sandbox: the read calls and
  filter shapes that work, how to follow several hops and join them in memory, how to read a hierarchy
  subtree, how to read completely instead of one page, and worked chains for exposure, notification
  impact, landed cost, traceability and competing demand. Use when a read needs more than one hop, a
  whole subtree, a complete list, or arithmetic across records. View, space and edge facts come from
  isc-model.
metadata:
  argument-hint: "business question + any externalId already resolved"
---

# Reading supply chain data in the sandbox

The sandbox runs read-only Python against the supply chain data models. It reads several hops in one
script, whole subtrees, complete lists rather than a page, and it computes — totals, comparisons and
date arithmetic that a single read cannot express. It is also where to look for a value that one read
did not show, before reporting it as absent.

Views, spaces, edge families, hierarchies and where each value lives are in **isc-model**. This skill is
how to read them.

## Setup

```python
from cognite.client import CogniteClient
from cognite.client.data_classes import filters as f
from cognite.client.data_classes.data_modeling import ViewId, NodeId, aggregations

client = CogniteClient()          # pre-authenticated, read-only
INST = "sp_isc_supply_chain_instances"  # every node and edge; never a view space
V = "v1.0.0"                        # the leading v is part of the version
```

`ViewId(space, "ViewName", V).as_property_ref("prop")` builds the `[space, "ViewName/v1.0.0", "prop"]`
reference that filters expect. Build it from a `ViewId` rather than typing the string.

## Procedure

1. **Plan the hops before writing code.** Write down the chain of records between the anchor and the
   answer, using isc-model. A chain of three hops is three reads, not three guesses.
2. **Write one script per chain, not one per hop.** One script that reads every level and joins them is
   faster and leaves a single output to reason over.
3. **Print compact rows** — externalId plus the fields you will cite. Printing whole SDK objects floods
   the output and the detail is then only a preview.
4. **Check the printed output against the question.** Every part covered? Any level that returned
   nothing? A level that returned exactly its limit (see *Reading completely*)?
5. **Compute in Python**, not by eye: totals, comparisons against dates, "most", "still valid".

If a name is needed and the record does not carry one, read it from the view isc-model points to. Rows
cited without names are not usable in an answer.

## The four reads

| Shape | Call |
|-------|------|
| One or more records by id | `instances.retrieve(nodes=[NodeId(INST, xid), ...], sources=[view])` |
| Records matching a filter | `instances.list(instance_type="node", sources=[view], filter=..., limit=...)` |
| Edges from an anchor | `instances.list(instance_type="edge", sources=[edge_view], filter=...)` |
| Count, sum, avg, min, max, per group | `instances.aggregate(view=vid, aggregates=..., group_by=[...], filter=..., instance_type="node")` |

`instances.query` sends one request that walks several steps server-side. It is worth it for a deep
chain from a single anchor; for a wide fan-out, several `list` calls joined in Python are easier to get
right and easier to read. Both are below.

## Filters

```python
mi = ViewId("sp_isc_material_management", "MaterialInventory", V)

# property equals / range
f.Equals(mi.as_property_ref("qtyOnHand"), 0)
f.Range(mi.as_property_ref("lastMovementDate"), lt=cutoff)   # cutoff: an ISO date string

# a direct relation: the value is a reference, never a bare string
f.Equals(mi.as_property_ref("warehouse"), {"space": INST, "externalId": wh_id})

# many ids at once — this is what turns N reads into one
f.In(mi.as_property_ref("materialId"), [{"space": INST, "externalId": m} for m in material_ids])

# edges: the type, plus the end your anchor sits on
f.And(
    f.Equals(["edge", "type"], {"space": "<edge type space>", "externalId": "<Start.edgeType>"}),
    f.Equals(["edge", "endNode"], {"space": INST, "externalId": anchor}),
)
```

The edge type space is not always the start view's space; isc-model lists it per edge family. Swapping
`startNode` for `endNode` turns a question around — "what does this supply" becomes "who supplies this"
— without changing the edge type.

**Null:** filtering on absent values is unreliable. Project the property and judge it in Python.

**As of a date:** filter `validFrom <= t` server-side, then keep the rows whose `validTo` is empty or
later than `t`:

```python
edge_view = ViewId("<edge view space>", "<EdgeView>", V)
rows = client.data_modeling.instances.list(
    instance_type="edge", sources=[edge_view], limit=-1,
    filter=f.And(
        f.Equals(["edge", "type"], {"space": type_space, "externalId": type_xid}),
        f.Equals(["edge", "startNode"], {"space": INST, "externalId": anchor}),
        f.Range(edge_view.as_property_ref("validFrom"), lte=as_of),
    ),
)
live = [e for e in rows
        if not (p := e.properties[edge_view]).get("validTo") or p["validTo"] > as_of]
```

`linkLastUpdatedTime` and `lastUpdated` are sync times, not business validity.

## Reading completely

Incomplete reads are the quiet failure: rows come back, the answer looks finished, and part of it is
missing.

- **A page is not the set.** `instances.list(..., limit=-1)` pages with cursors until the data runs out.
  Use it whenever the question says all, every, or a complete list.
- **A bounded read that returns exactly its limit is a warning, not a result.** The call stops at the
  limit without saying whether more existed. Either re-read with `limit=-1`, or say in the answer that
  the figure counts what was read.
- **Chunk large id lists.** An `In` filter holding more than about a thousand ids belongs in several
  calls, concatenated:

```python
def chunked(xs, size=1000):
    return [xs[i:i + size] for i in range(0, len(xs), size)]
```

- **`instances.query` pages too.** Its response carries `nextCursor` per step; a single response is one
  page of that step.
- **Count with `aggregate`, not with `len()` of a capped list.**

## Several hops: read level by level, join in memory

The shape that works for every chain: read all the edges of one level in one call, collect the ids at
the far end, read the next level with a single `In` filter over those ids, and join at the end. What
does not work is a read per row — it is slow and it quietly caps.

```python
ssm = ViewId("sp_isc_sourcing_procurement", "SupplierSuppliesMaterial", V)

def edges_from(edge_view, type_space, type_xid, anchors, role="startNode"):
    """All edges of one type whose `role` end is any of `anchors`."""
    out = []
    for chunk in chunked(list(anchors)):
        out += client.data_modeling.instances.list(
            instance_type="edge", sources=[edge_view], limit=-1,
            filter=f.And(
                f.Equals(["edge", "type"], {"space": type_space, "externalId": type_xid}),
                f.In(["edge", role], [{"space": INST, "externalId": a} for a in chunk]),
            ),
        )
    return out

level1 = edges_from(ssm, "sp_isc_sourcing_procurement", "Supplier.suppliesMaterial", [supplier])
materials = {e.end_node.external_id for e in level1}
# level2 = edges_from(<next edge view>, ..., materials, role="endNode") ... and so on
```

**Keep one row per edge.** Two records can be linked by more than one edge — two lanes between the same
material and destination, two supply records with different prices. Collecting into a dict keyed by the
pair of endpoints silently keeps the last one and stamps its cost or status onto every joined row. Build
a list of `(far_end_id, properties)` per anchor instead.

Each level multiplies the rows. Count what a level returned before expanding it, and say in the answer
when you aggregated rather than listed.

## Hierarchy subtrees

`parent` and the typed parent links give one level. Everything under a node, at any depth, comes from
`path`, which holds the ordered references from the root down to the node.

Read the anchor's own `path`, append the anchor itself if it is not already the last element, and use
that list as a prefix filter on the view. `path` and `name` live on the tree's **base view**
(isc-model's hierarchy table), so filter the base view, not the typed one.

```python
base = ViewId("sp_isc_organizational_foundation", "BusinessUnits", V)   # tree's base view
found = client.data_modeling.instances.retrieve(
    nodes=[NodeId(INST, anchor)], sources=[base]).nodes
path = [{"space": p["space"], "externalId": p["externalId"]}
        for p in (found[0].properties[base].get("path") or [] if found else [])]
if not path or path[-1]["externalId"] != anchor:
    path.append({"space": INST, "externalId": anchor})

subtree = client.data_modeling.instances.list(
    instance_type="node", sources=[base], limit=-1,
    filter=f.Prefix(base.as_property_ref("path"), path),
)
```

For the asset tree, `path` is inherited from CogniteAsset and is read through the FunctionalAsset view
in the same way. `path` is written by a background job after each change, so a node created moments ago
can have none; when the anchor has no path, fall back to walking `parent` level by level and say that
the tree may be incomplete.

## One request for a deep chain: `instances.query`

```python
payload = {
  "with": {
    "anchor": {"limit": 1, "nodes": {"filter": {"and": [
        {"equals": {"property": ["node", "externalId"], "value": anchor}},
        {"hasData": [{"type": "view", "space": a_space, "externalId": a_view, "version": V}]}]}}},
    "links":  {"limit": 1000, "edges": {"from": "anchor", "direction": "outwards", "maxDistance": 1,
        "filter": {"equals": {"property": ["edge", "type"],
                              "value": {"space": t_space, "externalId": t_xid}}}}},
    "targets": {"limit": 1000, "nodes": {"from": "links"}},
  },
  "select": {
    "anchor":  {"sources": [{"source": {"type": "view", "space": a_space, "externalId": a_view, "version": V},
                             "properties": ["name"]}]},
    "links":   {"sources": [{"source": {"type": "view", "space": e_space, "externalId": e_view, "version": V},
                             "properties": ["<edge properties>"]}]},
    "targets": {"sources": [{"source": {"type": "view", "space": t_view_space, "externalId": t_view, "version": V},
                             "properties": ["name"]}]},
  },
}
res = client.post(f"/api/v1/projects/{client.config.project}/models/instances/query", json=payload).json()
```

Guardrails, each one a rejection or a scan if ignored:

- `limit` belongs on the step, not inside `nodes` / `edges` (*unexpected field — nodes.limit*).
- Every `select.<step>.sources[]` needs an explicit `properties` list (*properties must not be null*).
  `["*"]` is accepted but returns every field of every row.
- The first step filters on `externalId` **and** `hasData` on its view; without `hasData` it scans.
- Follow a direct relation instead of an edge with a node step:
  `"through": {"source": {<view>}, "identifier": "<relation property>"}`, `"direction": "outwards"`, or
  `"inwards"` for the reverse — which is how you reach children that only point at their parent.
- Property references inside filters are `[space, "View/v1.0.0", "property"]`.

## Worked chains

Each is a sequence of edge levels read as above. The anchor role says which end the previous level's ids
sit on; the properties are what that level contributes to the answer. Edge type spaces and property
names are in isc-model.

| Question | Chain |
|----------|-------|
| Exposure if a supplier fails | Supplier →`suppliesMaterial`→ MaterialMaster (`unitCost`); materials as **end** of `TransportationLane.transportsMaterial` → lanes (`costPerTonne`); lanes as **end** of `Shipment.usesTransportationLane` → shipments (`delayReason`, `legSequence`); shipments →`executesReceipt`/`executesTransfer`→ scheduled records; retrieve those for order line and status |
| What a notification affects | MasterNotification →`linksEntity`→ work orders (`linkRole`, `impactCategory`, `severityAtLinkTime`) |
| Landed cost of a material | Material as **end** of `Supplier.suppliesMaterial` → `unitCost` per unit; material as **end** of `TransportationLane.transportsMaterial` → `costPerTonne` per lane. Join on the material and convert units before adding; they are priced per different units |
| What a shipment carries, and what it cost | Shipment →`usesTransportationLane`→ lanes (per-leg `plannedTransitDays`, `actualTransitDays`, `delayReason`, `actualCost`); lanes →`transportsMaterial`→ materials |
| Inbound traceability | Shipment →`executesReceipt`→ ScheduledReceipt (ASN, bill of lading, actual quantity, discrepancy on the edge); retrieve the receipts and follow `poLineItem` to the purchase order line |
| Demand on stock | MaterialInventory →`reservedForWorkOrderComponent`: one row per reservation with `quantityReserved` and `requirementDate`; compare the total against `qtyOnHand` |
| Subtree totals | Subtree by path prefix (above) for the ids, then `aggregate` or a list filtered with `In` over them |

## Aggregating

```python
res = client.data_modeling.instances.aggregate(
    view=vid, instance_type="node", space=INST,
    aggregates=aggregations.Count("externalId"),
    group_by=["<property>"], filter=filt,
)
```

`Sum`, `Avg`, `Min` and `Max` take a numeric property. Aggregates run on one view, so a figure that
spans a chain is computed in Python from the joined rows — say which rows it came from.

## When a read does not do what you expect

| Symptom | Cause |
|---------|-------|
| *View not found* | Version without the leading `v`, or the view is in another domain space |
| Unknown property, or a filter rejected | Guessed name. Take it from isc-model; `client.data_modeling.views.retrieve(ViewId(space, view, V))[0].properties.keys()` settles it in one call |
| Empty edge list | Wrong edge type space, wrong end (`startNode` vs `endNode`), or the anchor genuinely has none of that link |
| Rows returned but the field is empty | The value lives on the edge or on a linked record, not on this node — isc-model's *Where values live* |
| *Unexpected field — nodes.limit* | `limit` belongs on the query step |
| *properties must not be null* | A `select` source without a `properties` list |
| Exactly as many rows as the limit | Possibly truncated; re-read with `limit=-1` |
| Subtree empty but the node exists | `path` not materialized yet; walk `parent` instead |

An empty result from a correct read is an answer: name what was searched and where. Before concluding
that a value does not exist, check the one other place isc-model says it could live.
