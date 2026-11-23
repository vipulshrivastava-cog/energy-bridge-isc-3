-- Transformation: tr_btp_energy_bridge_purchase_order_confirmation
-- Source: {{ btpSeedDbName }}.purchase_order_confirmation (RAW)
-- Target: PurchaseOrderConfirmation ({{ isc_SourcingProcurementSchemaSpace }}:SourcingProcurement/{{dmVersion}})
-- Instance space: {{ isc_InstanceSpace }}


SELECT
    cast(`key` as STRING) as externalId,
    '{{ isc_InstanceSpace }}' as space,
    cast(`name` as STRING) as name,
    cast(`description` as STRING) as description,
    cast(`purchaseOrderId` as STRING) as purchaseOrderId,
    cast(`purchaseOrderItemId` as STRING) as purchaseOrderItemId,
    cast(`sequentialConfirmationNumber` as STRING) as sequentialConfirmationNumber,
    case when `poLineItem_externalId` is not null and trim(cast(`poLineItem_externalId` as STRING)) != ''
         then node_reference('{{ isc_InstanceSpace }}', cast(`poLineItem_externalId` as STRING))
         else null end as poLineItem,
    case when `supplier_externalId` is not null and trim(cast(`supplier_externalId` as STRING)) != ''
         then node_reference('{{ isc_InstanceSpace }}', cast(`supplier_externalId` as STRING))
         else null end as supplier,
    cast(`confirmationStatus` as STRING) as confirmationStatus,
    cast(`requestedDeliveryDate` as STRING) as requestedDeliveryDate,
    cast(`confirmedDeliveryDate` as STRING) as confirmedDeliveryDate,
    cast(`requestedShipDate` as STRING) as requestedShipDate,
    cast(`confirmedShipDate` as STRING) as confirmedShipDate,
    cast(`requestedQuantity` as DOUBLE) as requestedQuantity,
    cast(`confirmedQuantity` as DOUBLE) as confirmedQuantity,
    cast(`unitOfMeasure` as STRING) as unitOfMeasure,
    cast(`supplierMaterialNumber` as STRING) as supplierMaterialNumber,
    cast(`sendDate` as STRING) as sendDate,
    cast(`sendStatus` as STRING) as sendStatus,
    cast(`confirmationDateVariance` as INT) as confirmationDateVariance,
    cast(`confirmationQtyVariance` as DOUBLE) as confirmationQtyVariance,
    cast(`sourceId` as STRING) as sourceId,
    cast(`sourceContext` as STRING) as sourceContext,
    cast(`sourceCreatedTime` as STRING) as sourceCreatedTime,
    cast(`sourceUpdatedTime` as STRING) as sourceUpdatedTime,
    cast(`sourceCreatedUser` as STRING) as sourceCreatedUser,
    cast(`sourceUpdatedUser` as STRING) as sourceUpdatedUser
FROM
    `{{ btpSeedDbName }}`.`purchase_order_confirmation`
