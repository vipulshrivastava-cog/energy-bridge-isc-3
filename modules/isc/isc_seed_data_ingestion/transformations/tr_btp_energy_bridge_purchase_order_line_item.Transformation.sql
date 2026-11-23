-- Transformation: tr_btp_energy_bridge_purchase_order_line_item
-- Source: {{ btpSeedDbName }}.purchase_order_line_item + purchase_order_header (RAW)
-- Target: PurchaseOrderLineItem ({{ isc_SourcingProcurementSchemaSpace }}:SourcingProcurement/{{dmVersion}})
-- Instance space: {{ isc_InstanceSpace }}
-- The view spans the PurchaseOrderHeader and PurchaseOrderItem containers, so the item rows are
-- joined to their header. Header `purchasingCompletenessStatus` is not written (RAW holds text,
-- the view property is boolean).

SELECT
    cast(i.`key` as STRING) as externalId,
    '{{ isc_InstanceSpace }}' as space,
    cast(coalesce(h.`purchaseOrderId`, i.`purchaseOrderId`) as STRING) as purchaseOrderId,
    cast(i.`purchaseOrderId` as STRING) as purchaseOrderRef,
    cast(i.`purchaseOrderItemId` as STRING) as purchaseOrderItemId,
    cast(i.`currency` as STRING) as itemCurrency,
    cast(i.`itemDescription` as STRING) as itemDescription,
    cast(i.`unitOfMeasure` as STRING) as unitOfMeasure,
    cast(i.`quantityOrdered` as DOUBLE) as quantityOrdered,
    cast(i.`quantityReceived` as DOUBLE) as quantityReceived,
    cast(i.`netPrice` as DOUBLE) as netPrice,
    cast(i.`netOrderValue` as DOUBLE) as netOrderValue,
    cast(i.`requestedDeliveryDate` as STRING) as requestedDeliveryDate,
    cast(i.`requestedShipDate` as STRING) as requestedShipDate,
    cast(i.`itemStatus` as STRING) as itemStatus,
    cast(i.`isCompletelyDelivered` as BOOLEAN) as isCompletelyDelivered,
    cast(i.`isFinallyInvoiced` as BOOLEAN) as isFinallyInvoiced,
    cast(i.`purchaseOrderDeletionCode` as STRING) as purchaseOrderDeletionCode,
    cast(h.`purchasingOrganization` as STRING) as purchasingOrganization,
    cast(h.`orderDate` as STRING) as orderDate,
    cast(h.`createdByUser` as STRING) as createdByUser,
    cast(h.`companyCode` as STRING) as companyCode,
    cast(h.`currency` as STRING) as currency,
    cast(h.`totalNetValue` as DOUBLE) as totalNetValue,
    cast(h.`incoterms` as STRING) as incoterms,
    cast(h.`incotermsLocation` as STRING) as incotermsLocation,
    cast(h.`purchasingProcessingStatus` as STRING) as purchasingProcessingStatus,
    cast(h.`releaseIsNotCompleted` as BOOLEAN) as releaseIsNotCompleted,
    cast(h.`poStatus` as STRING) as poStatus,
    cast(h.`sourceId` as STRING) as sourceId,
    cast(h.`sourceContext` as STRING) as sourceContext,
    cast(h.`sourceCreatedTime` as STRING) as sourceCreatedTime,
    cast(h.`sourceUpdatedTime` as STRING) as sourceUpdatedTime,
    cast(h.`sourceCreatedUser` as STRING) as sourceCreatedUser,
    cast(h.`sourceUpdatedUser` as STRING) as sourceUpdatedUser,
    case when h.`supplier_externalId` is not null and trim(cast(h.`supplier_externalId` as STRING)) != ''
         then node_reference('{{ isc_InstanceSpace }}', cast(h.`supplier_externalId` as STRING))
         else null end as supplier,
    case when h.`shipTo_externalId` is not null and trim(cast(h.`shipTo_externalId` as STRING)) != ''
         then node_reference('{{ isc_InstanceSpace }}', cast(h.`shipTo_externalId` as STRING))
         else null end as headerShipTo,
    case when i.`material_externalId` is not null and trim(cast(i.`material_externalId` as STRING)) != ''
         then node_reference('{{ isc_InstanceSpace }}', cast(i.`material_externalId` as STRING))
         else null end as material,
    case when i.`shipTo_externalId` is not null and trim(cast(i.`shipTo_externalId` as STRING)) != ''
         then node_reference('{{ isc_InstanceSpace }}', cast(i.`shipTo_externalId` as STRING))
         else null end as shipTo,
    case when i.`supplierContract_externalId` is not null and trim(cast(i.`supplierContract_externalId` as STRING)) != ''
         then node_reference('{{ isc_InstanceSpace }}', cast(i.`supplierContract_externalId` as STRING))
         else null end as supplierContract,
    case when i.`purchaseRequisition_externalId` is not null and trim(cast(i.`purchaseRequisition_externalId` as STRING)) != ''
         then node_reference('{{ isc_InstanceSpace }}', cast(i.`purchaseRequisition_externalId` as STRING))
         else null end as purchaseRequisition
FROM
    `{{ btpSeedDbName }}`.`purchase_order_line_item` i
LEFT JOIN `{{ btpSeedDbName }}`.`purchase_order_header` h
    ON i.`purchaseOrderId` = h.`purchaseOrderId`
