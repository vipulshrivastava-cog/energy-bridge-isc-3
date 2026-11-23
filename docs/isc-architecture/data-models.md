# Data models

*How ISC's spaces, data models, containers, and views fit together — and the two patterns that sit on top: typed hierarchy views and edge views.*

**Who this is for:** trainees and instructors who want to understand how ISC is built, technically.

## Concepts

| Term | What it is |
|---|---|
| Space | The top-level, access-controlled container for a set of data models, containers, views, and instances. |
| Container | Defines the properties and storage for a node or edge type — the schema. |
| View | A queryable projection of one or more containers' properties, optionally filtered (e.g. by `declaredType`). |
| Direct relation | A property on a node or edge pointing at one other node. |
| Reverse direct relation | A view property that lists every node pointing back at this one through a named direct relation elsewhere (computed, not stored — e.g. a `Zone`'s `StorageBin` children, reversed off `StorageLocations.parent`). |
| Edge | A typed, queryable relationship instance between a start node and an end node, with its own properties — see [Direct relations and edges](#direct-relations-and-edges). |

## Spaces

Not everything in `modules/isc/` is a "domain" in the business sense — worth separating the categories before looking at spaces:

- **The 7 core domains** are the business-model domains from the [functional overview](../isc-functional-overview/overview.md#the-nine-domains-7-core-2-connect-layers), delivered end-to-end by ISC: Organizational Foundation, Material Management, Sourcing & Procurement, Shipment & Delivery, Planning & Forecasting, Customer Demand Fulfilment, and Technical Structure. This repo builds only **5 of those 7** — Customer Demand Fulfilment and Technical Structure have no space, container, or view here.
- **Asset Maintenance** isn't one of the 7 core domains — it's one of the 2 **connect layers**, where the core model wires to a customer's own plant/maintenance systems (`isc_connect_maintenance`). This repo builds it fully. The other connect layer, Manufacturing, is not part of this repo.
- **`sp_isc_platform`** isn't a business domain at all — it's a backend space holding background-job state (`FunctionSyncState` for hierarchy path-sync, `RawIngestState` for RAW ingest tracking), not supply-chain data.
- **`sp_isc_solution`** (the `isc_typed_model` data model) isn't a domain either — it's the concrete-view layer that projects each domain's hierarchy containers into typed per-level views (`Company`, `BusinessUnit`, `Warehouse`, etc.) — see [Typed hierarchy views](#typed-hierarchy-views) below.

So of the 9 total domains, this repo builds 6 (the 5 core domains + Asset Maintenance), plus the 2 non-domain support spaces (platform, typed model).

9 spaces, split by what they hold:

| Space | Holds |
|---|---|
| `sp_isc_solution` | The typed hierarchy views (see [Typed hierarchy views](#typed-hierarchy-views) below) |
| `sp_isc_platform` | Hierarchy path-sync and RAW-ingest state (`FunctionSyncState`, `RawIngestState` containers/views) |
| The instance space (default `sp_isc_supply_chain_instances`) | All business hierarchy and domain data instances |
| `sp_isc_organizational_foundation`, `sp_isc_material_management`, `sp_isc_sourcing_procurement`, `sp_isc_shipment_delivery`, `sp_isc_plan_forecast` | 5 upstream domain schema spaces — organizational foundation, material management, sourcing/procurement, logistics (shipment/delivery), planning/forecast — containers, views, and demo data all built |
| `sp_isc_asset_maintenance` | `isc_connect_maintenance` schema — upstream, fully built |

An edge view (see [Direct relations and edges](#direct-relations-and-edges)) lives in the schema space of one of the domains it connects (for example `MaterialReservation` is in the material management space). There is no separate edges space.

## Data models

8 `DataModel.yaml` files — all on the upstream side (see [Spaces](#spaces) above). The three downstream domains (customer demand fulfilment, technical structure, manufacturing) are not part of this repo:

| Data model | Space | Contains |
|---|---|---|
| `isc_typed_model` | `sp_isc_solution` | Concrete hierarchy views — `Company`, `BusinessUnit`, `CostCenter`, `GeoRegion`, `Country`, `City`, `Warehouse`, `Zone`, `StorageBin` |
| `IscPlatform` | `sp_isc_platform` | `FunctionSyncState`, `RawIngestState` |
| `OrganizationalFoundation`, `MaterialManagement`, `SourcingProcurement`, `ShipmentDelivery`, `PlanForecast` | 5 upstream domain spaces | The 5 built domains covered in [supply-chain](../isc-functional-overview/overview.md) |
| `AssetMaintenance` | `sp_isc_asset_maintenance` | `isc_connect_maintenance` module (upstream, fully built) |

## Containers and views

Standard pattern: each entity (e.g. `Supplier`, `MaterialLot`) has one container holding its properties and one view projecting those properties, both in the entity's domain schema space. Every container/view carries the same base source-tracking properties — `sourceId`, `sourceContext`, `sourceCreatedTime`, `sourceUpdatedTime`, `sourceCreatedUser`, `sourceUpdatedUser` — on top of its entity-specific fields. Total container and view counts are owned by [page 2](../isc-deployment/2-deploy-and-verify.md#4-check-fusion) — not repeated here.

Every data model and view carries its own version: data models use the `dmVersion` config variable, views use `viewVersion` — both `v1.0.0` today, set in `config.test.yaml`/`config.prod.yaml`.

Core views don't implement CDM views, but a couple relate to one: `MaterialMaster` and `Plan` each carry a typed direct relation to `cdf_cdm`'s `CogniteUnit` (`v1`) for their unit of measure. `isc_connect_maintenance`'s `FunctionalAsset` goes further and implements `cdf_cdm`'s `CogniteAsset` (`v1`) outright. `cdf_cdm` is the Cognite Core Data Model — a system space every CDF project provides by default, so this needs no extra setup.

## Typed hierarchy views

Hierarchy entities use a different pattern: one container per hierarchy tree in the domain space (e.g. `BusinessUnits` in `OrganizationalFoundation`) holds every level of that tree and a `declaredType` property. A concrete view per level — `Company`, `BusinessUnit`, `CostCenter` for the business hierarchy (similarly `GeoRegion`/`Country`/`City` for geography, `Warehouse`/`Zone`/`StorageBin` for storage) — lives in `sp_isc_solution`'s `isc_typed_model` data model, filtering the shared container on `declaredType` to project only the matching nodes. This is why hierarchy views live in a different space (`sp_isc_solution`) than their container (the domain schema space).

See [Build a new hierarchy](../isc-deployment/advanced/custom-hierarchies.md#build-a-new-hierarchy) for how to add a new typed view and trigger when extending a hierarchy.

## Direct relations and edges

8 typed edge views, split across two modules under `isc_edges/`:

| Edge view | Connects | Module |
|---|---|---|
| `SupplierSuppliesMaterial` | Supplier → Material | `isc_core_edges` |
| `LaneTransportsMaterial` | Transportation lane → Material | `isc_core_edges` |
| `LotStoredInBin` | Material lot → Storage bin | `isc_core_edges` |
| `ShipmentExecutesReceipt` | Shipment → Scheduled receipt | `isc_core_edges` |
| `ShipmentExecutesTransfer` | Shipment → Scheduled transfer | `isc_core_edges` |
| `MaterialReservation` | Material inventory → work order component | `isc_connect_edges` |
| `NotificationLinksEntity` | Master notification → the entity it impacts | `isc_connect_edges` |
| `UsesTransportationLane` | Shipment → Transportation lane | `isc_connect_edges` |


Three of the edges — reservation (`MaterialReservation`), notification links (`NotificationLinksEntity`), and transportation-lane usage (`UsesTransportationLane`) — are in `isc_connect_edges`, not `isc_core_edges`.

Every edge container is `usedFor: edge` and carries the same relationship properties on top of the standard source-tracking set: `relationType`, `relationStatus`, `validFrom`, `validTo` — plus entity-specific fields:

| Edge view | Extra properties beyond the common pack |
|---|---|
| `SupplierSuppliesMaterial` | `unitCost`, `currency`, `priorityRank`, `contractRef`, `minQuantity`, `maxQuantity`, `otifScore` (+ `otifScorePeriodStart`/`End`) |
| `LaneTransportsMaterial` | `priorityRank`, `minLotSize`/`maxLotSize`/`lotSizeUnit`, `costPerTonne`/`costCurrency`, `hazardousGoodsApproved`, `customsClearanceRequired` |
| `LotStoredInBin` | `qtyOnHand`, `qtyBlocked`, `lastUpdated`, `sourceSystem`, `linkLastUpdatedTime` |
| `ShipmentExecutesReceipt`, `ShipmentExecutesTransfer` | `quantity`/`quantityUnit`/`quantityType`/`uomConversionFactor`, ASN fields (`asnNumber`/`asnQty`/`asnDate`), BoL fields (`bolNumber`/`bolQty`/`bolDate`), `actualQty`, `receivedDate`, `actualDepartureDate`/`actualPickupDate`/`actualArrivalDate`, `goodsReceiptDocument`, `discrepancyQty`/`discrepancyReason`, `damageFlag`, `qualityHoldFlag`, `executionStatus`, direct relation to `material` — identical on both |
| `MaterialReservation` | `reservationNumber`, `quantityReserved`, `quantityUnit`, `reservationDate`, `requirementDate`, `sourceSystem`, `linkLastUpdatedTime` |
| `NotificationLinksEntity` | `linkRole`, `severityAtLinkTime`, `correlationId`, `impactCategory` |
| `UsesTransportationLane` | `plannedTransitDays`/`actualTransitDays`, `delayReason`, `actualCost`/`costCurrency`, `customsClearanceRequired`, `legSequence`/`legRole` |

## Who reads these models

These identifiers are bound in two places, both outside this module tree:

- The 3 Atlas agents each query via a `Query` tool scoped to location filter `loc_energy_bridge_supply_chain` (`providedAtRuntime` data models/instance spaces, not an inline baked-in list) — see [Atlas agents](atlas-agents-and-skills.md).
- `fn_btp_hierarchy` — the one Function that exists — takes space and view identifiers as runtime input on its workflow trigger (`view_space`, `platform_space`, `instance_spaces`, etc.), not generated constants baked in at build time — see [Functions and workflows](functions-and-workflows.md).

Renaming a space, data model, or view here can still break the location filter, trigger inputs, or transformations that reference the old identifier, so check those before renaming.

## Where to look

In Fusion: **Data models** for the 8 data models and their views, **Spaces** for the 9 spaces, **Containers** (under a space) for the underlying properties and indexes.
