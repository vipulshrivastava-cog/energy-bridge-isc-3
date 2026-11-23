-- Transformation: tr_btp_energy_bridge_purchase_requisition
-- Source: {{ btpSeedDbName }}.purchase_requisition (RAW)
-- Target: PurchaseRequisition ({{ isc_SourcingProcurementSchemaSpace }}:SourcingProcurement/{{dmVersion}})
-- Instance space: {{ isc_InstanceSpace }}


SELECT
    cast(`key` as STRING) as externalId,
    '{{ isc_InstanceSpace }}' as space,
    cast(`name` as STRING) as name,
    cast(`description` as STRING) as description,
    cast(`materialRequestId` as STRING) as materialRequestId,
    cast(`itemNumber` as STRING) as itemNumber,
    cast(`materialId` as STRING) as materialId,
    case when `workOrderId_externalId` is not null and trim(cast(`workOrderId_externalId` as STRING)) != ''
         then node_reference('{{ isc_InstanceSpace }}', cast(`workOrderId_externalId` as STRING))
         else null end as workOrderId,
    case when `material_externalId` is not null and trim(cast(`material_externalId` as STRING)) != ''
         then node_reference('{{ isc_InstanceSpace }}', cast(`material_externalId` as STRING))
         else null end as material,
    case when `supplier_externalId` is not null and trim(cast(`supplier_externalId` as STRING)) != ''
         then node_reference('{{ isc_InstanceSpace }}', cast(`supplier_externalId` as STRING))
         else null end as supplier,
    cast(`quantityRequested` as DOUBLE) as quantityRequested,
    cast(`neededByDateTime` as STRING) as neededByDateTime,
    cast(`requestDateTime` as STRING) as requestDateTime,
    cast(`unitEstimatedPrice` as DOUBLE) as unitEstimatedPrice,
    cast(`materialRequestType` as STRING) as materialRequestType,
    cast(`processingStatus` as STRING) as processingStatus,
    cast(`prReleaseStatus` as STRING) as prReleaseStatus,
    cast(`prOrigin` as STRING) as prOrigin,
    cast(`purchasingGroup` as STRING) as purchasingGroup,
    cast(`baseUnit` as STRING) as baseUnit,
    cast(`currency` as STRING) as currency,
    cast(`sourceId` as STRING) as sourceId,
    cast(`sourceContext` as STRING) as sourceContext,
    cast(`sourceCreatedTime` as STRING) as sourceCreatedTime,
    cast(`sourceUpdatedTime` as STRING) as sourceUpdatedTime,
    cast(`sourceCreatedUser` as STRING) as sourceCreatedUser,
    cast(`sourceUpdatedUser` as STRING) as sourceUpdatedUser
FROM
    `{{ btpSeedDbName }}`.`purchase_requisition`
