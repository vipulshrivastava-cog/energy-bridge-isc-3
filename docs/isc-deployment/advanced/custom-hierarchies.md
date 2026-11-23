# Custom hierarchies

*How ISC handles tree-shaped data such as business units, locations, and how to load one, build a new one, or clear one.*

> [!NOTE]
> For data engineers and solution architects. Read it when you load data into an existing ISC hierarchy, add a new one, or clear one. For the business view, see [Organizational Foundation](../../isc-functional-overview/domains/organizational-foundation.md).

## How it works

A hierarchy is a tree of parent and child nodes, used to roll up and drill down. You load each node's own fields and a single `parent` link. A deployed workflow then runs `fn_btp_hierarchy`, which fills in `root`, `path` and `pathLastUpdatedTime`. That lets agents and apps read a whole branch in one query, without walking the tree one step at a time.

```mermaid
flowchart LR
    W["You: write fields + parent"] --> N["Nodes in your instance space"]
    N --> T["Trigger on data changes"] --> F["fn_btp_hierarchy"] --> N
```

**In scope:** `BusinessUnits`, `GeoLocations`, and `StorageLocations` (the warehouse tree).
**Out of scope:** asset trees. `FunctionalAsset` uses the platform's own path handling, not `fn_btp_hierarchy`.

## Rules

| # | Rule | What it means |
|---|---|---|
| 1 | Use ISC's own containers | Keep hierarchy, search and provenance on `sp_*` containers. Don't use `cdf_cdm` types such as `CogniteAsset` for supply-chain trees. |
| 2 | Separate the writers | Ingest writes `parent` and the plain fields. Path sync writes `root` and `path`. Never write `children`. |
| 3 | Let the workflow run path sync | A data-change trigger starts `wf_btp_hierarchy_path`. Don't call the function by hand in normal operation. |
| 4 | Query the concrete views | Agents and apps use views such as `City`, filtered by `declaredType`. The interface views (`GeoLocations`, `StorageLocations`) are for path sync and platform tools. |
| 5 | Mind the limits | A `path` holds up to 100 levels. Keep one hierarchy under about 10,000 nodes. |
| 6 | Tune only with the ISC team | Change `batchSize`, `batchTimeout` or `chunk_size` only after agreeing it with the ISC team. |

## Scale and tuning

| Nodes in a tree | Path sync under the defaults |
|---|---|
| Up to about 10,000 | A few minutes after ingest. This is the recommended range. |
| Over 10,000 | Up to 3 to 5 minutes to rebuild `root` and `path`. Talk to the ISC team before growing further. |

Load in bulk, with batched upserts or a SQL transform, rather than as many single-row writes. Fewer change events means faster convergence.

Each hierarchy's trigger carries these settings. They ship with validated defaults:

| Parameter | Default | What it does |
|---|---|---|
| `batchSize` | 100 | The most change notifications CDF groups into one workflow run. |
| `batchTimeout` | 60 s | How long CDF waits to fill a batch before starting anyway. |
| `chunk_size` | 200 | Changed nodes `fn_btp_hierarchy` handles per page within a run. |

```yaml
input:
  chunk_size: 200
  max_runtime_seconds: 480
triggerRule:
  batchSize: 100
  batchTimeout: 60
```

The example is the GeoLocation trigger, `wf_trigger_btp_hierarchy_path_geo_locations.WorkflowTrigger.yaml` in `isc_core/workflows/`. Treat `max_runtime_seconds` and `sync_lock` the same way as the three above.

## Use an existing hierarchy

### 1. Ingest

Write to your instance space (`isc_InstanceSpace`), through the concrete or interface view.

| Field | Who writes it | When |
|---|---|---|
| `name`, `description`, domain fields, provenance | You | On create and update |
| `declaredType` (points to a `DeclaredTypes` row) | You | On create and update |
| `parent` | You | On create and update. `null` for a root. |
| `root`, `path`, `pathLastUpdatedTime` | `fn_btp_hierarchy` | After ingest, through the trigger |
| `children` | Nobody | Calculated at query time |

Load parents before children, or accept that a child's parent resolves on a later pass.

- **For ongoing loads,** use the generated typed write classes from the shipped views, or the API.
- **For a large first load,** use a two-pass SQL transform: first the fields and `declaredType`, then `parent`.

### 2. Let path sync run

After ingest, the trigger on that view starts `wf_btp_hierarchy_path`, which runs `fn_btp_hierarchy` in `path_sync_cursor` mode. Allow a few minutes, and up to 3 to 5 for trees over 10,000 nodes.

### 3. Query

| Need | How |
|---|---|
| All nodes of one level | The concrete view with a `declaredType` filter (`ProductFamily`, `Country`, …) |
| Everything under a node | Filter where `path` starts with that ancestor, after path sync |
| Direct children | Filter on `parent`, or use the view's `children` relation |
| An agent hop | Concrete types such as `ProductFamily` or `City`, not interface views |

## Build a new hierarchy

A wholly new tree, such as a customer-specific cost-center tree, is new capability. Build it in a **new customer module** (`modules/<name>/`, outside `modules/isc/`). Use `isc_connect_maintenance` only if the tree is specifically wiring to the tenant's maintenance data. Either way, point your trigger at the shared `fn_btp_hierarchy` function and `wf_btp_hierarchy_path` workflow by their shipped IDs. Don't copy them.

### A. The data model, in your module

| Step | Action |
|---|---|
| A1 | Create a container in your own schema space with `parent`, `root`, `path`, `pathLastUpdatedTime`, `name`, provenance and your domain fields. |
| A2 | Create an interface view on it. This is the path-sync target. |
| A3 | Add `DeclaredTypes` rows for each level, following the shipped `DeclaredTypes` view. |
| A4 | Create concrete views that implement the interface view, each with a `declaredType` filter. |
| A5 | Map one typed parent per concrete view to the container's `parent` field. |
| A6 | Register the interface view in your own data model. |
| A7 | Register the concrete views in your module's typed surface, as `isc_typed_model` does for `isc_core`. |

### B. The shared runtime (reference only)

| What | Where |
|---|---|
| Function | `modules/isc/isc_core/functions/fn_btp_hierarchy/` |
| Path workflow | `modules/isc/isc_core/workflows/wf_btp_hierarchy_path*.yaml` |
| Platform state | `FunctionSyncState` and `RawIngestState` in `sp_isc_platform` |

### C. The trigger, in your module

| Step | Action |
|---|---|
| C1 | Add a path workflow trigger (`dataModeling`, `noBackfill`, empty `select`) pointed at the shared `wf_btp_hierarchy_path` workflow. |
| C2 | Point it at your interface view and your instance space. |
| C3 | Set its authentication (a service principal). |
| C4 | Optional: a RAW table and landing transform for batch sources. |
| C5 | Optional: bootstrap SQL for a one-off or large first load. |


## Clear or remove data

**Clear the instances in a hierarchy** (to reload or correct it). The model and trigger stay deployed.

1. Pause the hierarchy's path trigger.
2. Wait for running path workflows to finish.
3. Delete the hierarchy's instances from your instance space, leaves first or by a known `externalId` prefix.
4. Resume the trigger when you're ready to ingest again.

Deleting an ancestor makes its direct children new roots at the next path sync. Delete from the top down, or remove the whole subtree on purpose.

**Remove a hierarchy you built.** Pause and delete its trigger, delete its instances, then remove the concrete views, the interface view, the container and the `DeclaredTypes` rows you added. All of it is in your own module.

## Check it worked

After ingest and a few minutes of path sync, nodes in your instance space show a non-empty `root` and `path` on the hierarchy view.

## If it fails

| Symptom | Likely cause | What to do |
|---|---|---|
| `path` is empty after ingest | The trigger isn't deployed or is paused, or `noBackfill` means static data never ran | Deploy the trigger, then run a bootstrap path sync. |
| Path sync is slow at 10,000+ nodes | A large tree on default settings | Allow 3 to 5 minutes. Contact the ISC team if it takes longer, before tuning. |
| Nodes appear in the wrong concrete view | Missing or wrong `declaredType` | Fix the ingest and check the `DeclaredTypes` rows. |
| Path sync never finishes | An echo loop or a backlog | Check the function logs for `path_echo_skip`, and reduce ingest churn. |

**Next:** [Back to the implementation overview](../1-overview-and-prerequisites.md)
