# Load the seed data

*`cdf deploy` creates the models and the empty tables, but no data. Run the seed workflow by hand to load the Energy Bridge demo graph.*

**Before you start:** `fn_btp_hierarchy` shows **Ready** in Fusion ([Build, deploy, and verify](./2-deploy-and-verify.md)). Starting earlier risks the hierarchy-path triggers firing against a half-synced graph once the hierarchy data lands.

## Where the seed workflow comes from

The seed workflow, its RAW tables, and its transformations ship in the `isc_seed_data_ingestion` module — **demo and training data only**, built around a dummy client, Energy Bridge. It's not part of the core supply-chain schema. It's already in `environment.selected` in this repo's `config.test.yaml`/`config.prod.yaml`, and it's deployed in the same `cdf build` as `isc_core` — the transformations read spaces and views that `isc_core` defines, so a build without `isc_core` fails with `Unknown reference to spaces` or `Unknown reference to views`.

## Decide first

| Do you want the demo graph? | Then |
|---|---|
| Yes — training, or trying the Atlas agents on sample data | Run this page. |
| No — you want an empty schema to load your own data into | Skip it, and remove `modules/isc/isc_seed_data_ingestion` from `selected` in `config.<env>.yaml`. The Atlas agents' sample questions will find nothing until some data is ingested. |

> [!WARNING]
> Don't load the demo graph into a project that holds real data — the sample IDs are fictional (Energy Bridge) and will mix with real records.

## Steps

1. In Fusion, open **Workflows**, then `wf_btp_energy_bridge_data`.
2. Start version `1` manually.
3. Wait for the status **COMPLETED**.

## What it does

It runs 32 transformations against 29 RAW seed tables plus an inline `DeclaredTypes` catalog. These aren't a strict front-to-back sequence — they run as a dependency graph, with a handful of root tasks (`DeclaredTypes`, both `FunctionalAsset` enrichment tasks, `Supplier`, `MasterNotification`) starting immediately and everything else building outward from there (hierarchies, then materials, work orders, shipments, purchase orders, and their relationships). Once the hierarchy nodes land, the `wf_btp_hierarchy_path` triggers fire separately to sync `root`/`path` on them — see [Functions and workflows](../isc-architecture/functions-and-workflows.md).

## What the demo graph contains

29 RAW seed tables covering the built domains (Organizational Foundation, Material Management, Asset Maintenance, Sourcing & Procurement, Shipment & Delivery, Planning & Forecasting) — small enough to explore by hand.The Atlas agents' sample questions rely on this data.

## Check it worked

The run status is **COMPLETED**, and **Data explorer** shows instances on views such as `MaterialMaster`, `PurchaseOrderLineItem`, and `Shipment`.

## If it fails

| Symptom | Cause | Fix |
|---|---|---|
| The run fails at the start | `fn_btp_hierarchy` is not Ready yet | Wait for it to show Ready, then start again. |
| A task fails mid-run | A transformation error | Open that transformation's logs. Don't treat a failed run as a loaded graph. |
| `cdf build` reports `Unknown reference to spaces` or `views` for seed transformations | `isc_seed_data_ingestion` was built without `isc_core` | Build with the full `selected` list, so `isc_core` is in the same build. |
| The run completes but Data explorer is empty | Looking in the wrong space | Check `isc_InstanceSpace` in `config.<env>.yaml` (shipped as `sp_isc_supply_chain_instances`). |

## Re-running

Re-run version `1` any time you want to refresh or reload the demo graph.

## What's next

- Back to the [implementation overview](./1-overview-and-prerequisites.md), or explore the model in [isc-architecture](../isc-architecture/data-models.md).
