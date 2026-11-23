---
name: isc-model
description: >-
  What exists where in the supply chain data models: domains, view spaces, views, edge families with their
  properties, hierarchies, and where each kind of value lives. Load before the first data read, whatever
  the read method. Holds model facts only — what exists and where each value lives, not how to read it.
metadata:
  argument-hint: "business noun, view externalId or relationship (e.g. reservation, lane freight, cost centre tree)"
---

# Supply chain data model

| Constant | Value |
|----------|-------|
| Instance space | `sp_isc_supply_chain_instances`. Every node and edge lives here. It is never a view space; use it only in node and edge references. |
| View version | `v1.0.0` for every view (the leading `v` is part of the version) |
| Edge type space | Listed per edge type below; it is not always the start view's space |
| Shared edge properties | Every edge view has `relationType`, `relationStatus`, `validFrom`, `validTo` |

## Domains, spaces and views

| Domain | View space | Data model | Node views | Edge views |
|--------|-----------|-----------|------------|------------|
| Organization | `sp_isc_organizational_foundation` | `OrganizationalFoundation` | BusinessUnits, GeoLocations, MasterNotification, DeclaredTypes | NotificationLinksEntity |
| Material | `sp_isc_material_management` | `MaterialManagement` | MaterialMaster, MaterialInventory, MaterialLot, MaterialAlternative, InventoryQualityResult, StorageLocations | MaterialReservation, LotStoredInBin |
| Maintenance | `sp_isc_asset_maintenance` | `AssetMaintenance` | FunctionalAsset, WorkOrder, WorkOrderComponent | |
| Procurement | `sp_isc_sourcing_procurement` | `SourcingProcurement` | Supplier, SupplierFacility, SupplierContract, SupplierItemRecord, PurchaseOrderLineItem, PurchaseOrderConfirmation, PurchaseRequisition | SupplierSuppliesMaterial |
| Logistics | `sp_isc_shipment_delivery` | `ShipmentDelivery` | Shipment, TransportationLane, ScheduledReceipt, ScheduledTransfer, StockTransferOrder | LaneTransportsMaterial, UsesTransportationLane, ShipmentExecutesReceipt, ShipmentExecutesTransfer |
| Planning | `sp_isc_plan_forecast` | `PlanForecast` | Forecast, Plan | |
| Typed hierarchy | `sp_isc_solution` | `isc_typed_model` | Company, BusinessUnit, CostCenter, GeoRegion, Country, City, Warehouse, Zone, StorageBin | |

`IscPlatform` (`sp_isc_platform`: FunctionSyncState, RawIngestState) holds internal sync state; it never answers a business question.

Only the views above exist; when unsure of a property name, read the view's definition before filtering on it.

## What one record is

| View | One record is | Watch for |
|------|---------------|-----------|
| PurchaseOrderLineItem | One purchase order line, carrying its header fields | PO number `purchaseOrderId`, line `purchaseOrderItemId`; status history `poStatus`, `previousPoStatus`, `statusChangedAt`; date changes `requestedDeliveryDate`, `previousRequestedDeliveryDate`, `requestedDeliveryDateChangeDays` |
| MaterialInventory | The stock of one material in one warehouse (not a lot) | `materialId` and `warehouse` are direct relations; `qtyOnHand`, `safetyStock`, `reorderPoint`, `lastMovementDate` |
| MaterialLot | One lot of a material | Its quantity per bin is on the `LotStoredInBin` edge, not on the lot |
| Shipment | One shipment header | ETA fields (`estimatedArrivalDate`, `previousEstimatedArrivalDate`, `estimatedArrivalDateChangeDays`) record ETA changes. Per-leg transit times and `delayReason` are on the `UsesTransportationLane` edge |
| ScheduledReceipt / ScheduledTransfer | One planned inbound or internal movement line | What actually happened (ASN, bill of lading, actual quantities and dates) is on the `ShipmentExecutes*` edge from the shipment |
| MasterNotification | One event (breakdown, delay, change) | It has no direct links; what it affects is reached through edges (see Edge families) |

## Edge families

Start view → end view. Read cost, quantity, status and dates from the edge, not from either end node.

| Edge type (type space) | Start → end | Edge view (view space) | Key edge properties | Property on start / end node |
|------------------------|-------------|------------------------|---------------------|------------------------------|
| `MaterialInventory.reservedForWorkOrderComponent` (`sp_isc_material_management`) | MaterialInventory → WorkOrderComponent | MaterialReservation (`sp_isc_material_management`) | `quantityReserved`, `quantityUnit`, `requirementDate`, `reservationDate`, `reservationNumber` | `reservedForWorkOrderComponent` / `materialReservationsFromLots` |
| `MaterialLot.storedInBin` (`sp_isc_material_management`) | MaterialLot → StorageBin | LotStoredInBin (`sp_isc_material_management`) | `qtyOnHand`, `qtyBlocked`, `lastUpdated` | `storedInBins` / `lotsStored` |
| `TransportationLane.transportsMaterial` (`sp_isc_shipment_delivery`) | TransportationLane → MaterialMaster | LaneTransportsMaterial (`sp_isc_shipment_delivery`) | `costPerTonne`, `costCurrency`, `minLotSize`, `maxLotSize`, `lotSizeUnit`, `priorityRank`, `hazardousGoodsApproved`, `customsClearanceRequired` | `transportsMaterial` / `transportedOnLanes` |
| `Shipment.usesTransportationLane` (`sp_isc_shipment_delivery`) | Shipment → TransportationLane | UsesTransportationLane (`sp_isc_shipment_delivery`) | `legSequence`, `legRole`, `plannedTransitDays`, `actualTransitDays`, `delayReason`, `actualCost`, `costCurrency`, `customsClearanceRequired` | `usesTransportationLane` / `usedByShipments` |
| `Shipment.executesReceipt` (`sp_isc_shipment_delivery`) | Shipment → ScheduledReceipt | ShipmentExecutesReceipt (`sp_isc_shipment_delivery`) | `quantity`, `quantityUnit`, `asnNumber`, `asnQty`, `bolNumber`, `bolQty`, `actualQty`, `receivedDate`, `actualArrivalDate`, `discrepancyQty`, `discrepancyReason`, `damageFlag`, `qualityHoldFlag`, `executionStatus`, `material` | `executesReceipt` / `executedByShipments` |
| `Shipment.executesTransfer` (`sp_isc_shipment_delivery`) | Shipment → ScheduledTransfer | ShipmentExecutesTransfer | same | `executesTransfer` / `executedByShipments` |
| `Supplier.suppliesMaterial` (`sp_isc_sourcing_procurement`) | Supplier → MaterialMaster | SupplierSuppliesMaterial (`sp_isc_sourcing_procurement`) | `unitCost`, `currency`, `priorityRank`, `minQuantity`, `maxQuantity`, `contractRef`, `otifScore`, `otifScorePeriodStart`, `otifScorePeriodEnd` | `suppliesMaterial` / `suppliedBySuppliers` |
| `MasterNotification.linksEntity` (`sp_isc_organizational_foundation`) | MasterNotification → WorkOrder | NotificationLinksEntity (`sp_isc_organizational_foundation`) | `linkRole`, `severityAtLinkTime`, `impactCategory`, `correlationId` | `linksEntity` / `linkedFromNotifications` |

**Direction.** To start from the end node (for example from a work order component to the inventory reserved for
it), use the same edge type with the anchor as the end node.

**As-of validity.** For "active", "current", "valid on" or "as of": `validFrom <= t` and (`validTo` is empty or
`validTo > t`). `linkLastUpdatedTime` and `lastUpdated` are sync times, not business dates.

## Direct relations that are easy to miss

Some links exist only on the child. To go from parent to child, filter the child view on the relation.

| From | To | How |
|------|----|-----|
| MaterialMaster or Warehouse | stock | Filter MaterialInventory on `materialId` and/or `warehouse` |
| MaterialMaster | its alternatives | Filter MaterialAlternative on `originalMaterial`; read `alternativeMaterial`, `alternativeType`, `priority`, `quantityConversionFactor`, `isActive`. The reverse `materialAlternatives` on MaterialMaster covers only `originalMaterial` |
| PurchaseOrderLineItem | its receipts | ScheduledReceipt `poLineItem` (reverse `scheduledReceipts`); the plan-to-order link is this direct relation, not an edge |
| StockTransferOrder | its transfers | ScheduledTransfer `stockTransferOrder` (reverse `scheduledTransfers`) |
| Supplier | its receipts | Filter ScheduledReceipt on `supplier` |
| WorkOrder | its components | WorkOrderComponent `workOrder` (reverse `components`) |
| FunctionalAsset | its city and country | `belongtoCity` → City `country` → Country |
| FunctionalAsset | its cost centre | `belongtoCostCenter` → CostCenter |
| Purchase order line | its contract | `supplierContract` → SupplierContract (`contractPrice`, `validFrom`, `validTo`, `contractStatus`) |

## Hierarchies

Four trees. In each, a base view holds `name`, `parent`, `root` and `path`; the typed views in `sp_isc_solution`
are kinds of node in that tree and add only type-specific fields and links.

| Tree | Base view (space) | Typed views (`sp_isc_solution`) and their parent link |
|------|-------------------|-------------------------------------------------------|
| Organization | BusinessUnits (`sp_isc_organizational_foundation`) | Company; BusinessUnit (`company`); CostCenter (`businessUnit`) |
| Geography | GeoLocations (`sp_isc_organizational_foundation`) | GeoRegion (`parent_geo_region`); Country (`geo_region`); City (`country`) |
| Storage | StorageLocations (`sp_isc_material_management`) | Warehouse; Zone (`warehouse`); StorageBin (`zone`) |
| Assets | FunctionalAsset (`sp_isc_asset_maintenance`), which implements CogniteAsset | none; `parent`, `root` and `path` come from CogniteAsset |

- **Names live on the base view.** Typed views have no `name`: read the name of a City, Country, CostCenter,
  Warehouse or StorageBin from GeoLocations, BusinessUnits or StorageLocations, using the same node.
- **One level vs all levels.** A typed parent link (for example CostCenter `businessUnit`) or `parent` gives direct
  children only. For everything under a node, at any depth, use `path`.
- **`path`** is the ordered list of node references from the root down to the node. The descendants of a node are
  the nodes whose `path` starts with that node's `path` (ending with the node itself). It is written by a background
  job after each change, so a node created moments ago can lack it.
- Do not mix trees in one read.

## Where values live

| Value | Read it from | Not from |
|-------|--------------|----------|
| Freight cost and lot sizes for a material on a lane | LaneTransportsMaterial edge | the TransportationLane node |
| Supplier price, quantity range, priority and on-time score for a material | SupplierSuppliesMaterial edge | a supplier or material property |
| Contract price and validity | SupplierContract (via `supplierContract` on the PO line, or filter on `supplier` / `materialId`) | `contractRef` text alone |
| Why a shipment is late, and by how much per leg | UsesTransportationLane edge (`delayReason`, `plannedTransitDays` vs `actualTransitDays`) | Shipment ETA change fields |
| What arrived (ASN, bill of lading, actual quantity, damage, discrepancy) | ShipmentExecutes* edges | the scheduled record |
| Stock of a material | MaterialInventory (per warehouse); lot quantity per bin on LotStoredInBin | MaterialMaster |
| Reserved quantity | MaterialReservation edge | MaterialInventory |
| What a notification affects | NotificationLinksEntity (work orders) | MasterNotification properties |
| Name of a typed hierarchy node | Base view of its tree | the typed view |

## Common paths across several records

| Question | Path |
|----------|------|
| Inventory backing a work order | WorkOrder → `components` → WorkOrderComponent ← reservation edges (end node) ← MaterialInventory |
| Notifications on a work order | WorkOrder `linkedFromNotifications` (NotificationLinksEntity) |
| What a notification affects | MasterNotification → `linksEntity` → WorkOrder |
| Supplier failure exposure | Supplier → `suppliesMaterial` → MaterialMaster → `transportedOnLanes` → TransportationLane → `usedByShipments` → Shipment → `executesReceipt` / `executesTransfer` → scheduled records |
| Landed cost inputs for a material | SupplierSuppliesMaterial (`unitCost` per unit) plus LaneTransportsMaterial (`costPerTonne`); convert units before adding |
| Alternates with stock | MaterialAlternative (`originalMaterial`) → `alternativeMaterial` → MaterialInventory (`materialId`, `warehouse`) → its reservation edges |
| Shipment against plan | Shipment → `executesReceipt` / `executesTransfer` → scheduled record → `poLineItem` or `stockTransferOrder` |
| Assets by country | FunctionalAsset `belongtoCity` → City `country` → Country; names from GeoLocations |
