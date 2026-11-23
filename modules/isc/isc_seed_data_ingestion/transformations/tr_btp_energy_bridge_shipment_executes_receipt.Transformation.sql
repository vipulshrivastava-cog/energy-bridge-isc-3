-- Transformation: tr_btp_energy_bridge_shipment_executes_receipt
-- Source: {{ btpSeedDbName }}.shipment_executes_receipt (RAW)
-- Target: ShipmentExecutesReceipt (edge Shipment.executesReceipt) ({{ isc_ShipmentDeliverySchemaSpace }}:ShipmentDelivery/{{dmVersion}})
-- Instance space: {{ isc_InstanceSpace }}


SELECT
    cast(`key` as STRING) as externalId,
    case when `startShipment_externalId` is not null and trim(cast(`startShipment_externalId` as STRING)) != ''
         then node_reference('{{ isc_InstanceSpace }}', cast(`startShipment_externalId` as STRING))
         else null end as startNode,
    case when `endScheduledReceipt_externalId` is not null and trim(cast(`endScheduledReceipt_externalId` as STRING)) != ''
         then node_reference('{{ isc_InstanceSpace }}', cast(`endScheduledReceipt_externalId` as STRING))
         else null end as endNode,
    node_reference('{{ isc_ShipmentDeliverySchemaSpace }}', 'Shipment.executesReceipt') as type,
    cast(`name` as STRING) as name,
    cast(`description` as STRING) as description,
    cast(`relationType` as STRING) as relationType,
    cast(`relationStatus` as STRING) as relationStatus,
    cast(`validFrom` as STRING) as validFrom,
    cast(`validTo` as STRING) as validTo,
    cast(`quantity` as DOUBLE) as quantity,
    cast(`quantityUnit` as STRING) as quantityUnit,
    cast(`quantityType` as STRING) as quantityType,
    cast(`asnNumber` as STRING) as asnNumber,
    cast(`asnQty` as DOUBLE) as asnQty,
    cast(`asnQtyUnit` as STRING) as asnQtyUnit,
    cast(`asnDate` as STRING) as asnDate,
    cast(`bolNumber` as STRING) as bolNumber,
    cast(`bolQty` as DOUBLE) as bolQty,
    cast(`bolQtyUnit` as STRING) as bolQtyUnit,
    cast(`bolDate` as STRING) as bolDate,
    cast(`actualQty` as DOUBLE) as actualQty,
    cast(`actualQtyUnit` as STRING) as actualQtyUnit,
    cast(`receivedDate` as STRING) as receivedDate,
    cast(`actualDepartureDate` as STRING) as actualDepartureDate,
    cast(`actualPickupDate` as STRING) as actualPickupDate,
    cast(`actualArrivalDate` as STRING) as actualArrivalDate,
    cast(`goodsReceiptDocument` as STRING) as goodsReceiptDocument,
    cast(`discrepancyQty` as DOUBLE) as discrepancyQty,
    cast(`discrepancyReason` as STRING) as discrepancyReason,
    cast(`damageFlag` as BOOLEAN) as damageFlag,
    cast(`qualityHoldFlag` as BOOLEAN) as qualityHoldFlag,
    cast(`executionStatus` as STRING) as executionStatus,
    case when `material_externalId` is not null and trim(cast(`material_externalId` as STRING)) != ''
         then node_reference('{{ isc_InstanceSpace }}', cast(`material_externalId` as STRING))
         else null end as material,
    cast(`containerNumber` as STRING) as containerNumber,
    cast(`sourceId` as STRING) as sourceId,
    cast(`sourceContext` as STRING) as sourceContext,
    cast(`sourceCreatedTime` as STRING) as sourceCreatedTime,
    cast(`sourceUpdatedTime` as STRING) as sourceUpdatedTime,
    cast(`sourceCreatedUser` as STRING) as sourceCreatedUser,
    cast(`sourceUpdatedUser` as STRING) as sourceUpdatedUser
FROM
    `{{ btpSeedDbName }}`.`shipment_executes_receipt`
