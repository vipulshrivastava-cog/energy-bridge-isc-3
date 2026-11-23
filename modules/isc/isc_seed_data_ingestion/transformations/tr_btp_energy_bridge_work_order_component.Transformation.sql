-- Transformation: tr_btp_energy_bridge_work_order_component
-- Source: {{ btpSeedDbName }}.work_order_component (RAW)
-- Target: WorkOrderComponent ({{ isc_AssetMaintenanceSchemaSpace }}:AssetMaintenance/{{dmVersion}})
-- Instance space: {{ isc_InstanceSpace }}


SELECT
    cast(`key` as STRING) as externalId,
    '{{ isc_InstanceSpace }}' as space,
    cast(`name` as STRING) as name,
    cast(`description` as STRING) as description,
    case when `workOrder_externalId` is not null and trim(cast(`workOrder_externalId` as STRING)) != ''
         then node_reference('{{ isc_InstanceSpace }}', cast(`workOrder_externalId` as STRING))
         else null end as workOrder,
    case when `material_externalId` is not null and trim(cast(`material_externalId` as STRING)) != ''
         then node_reference('{{ isc_InstanceSpace }}', cast(`material_externalId` as STRING))
         else null end as material,
    cast(`materialNumber` as STRING) as materialNumber,
    cast(`reservationRequirementNumber` as STRING) as reservationRequirementNumber,
    cast(`reservationItemNumber` as STRING) as reservationItemNumber,
    cast(`activityNumber` as STRING) as activityNumber,
    cast(`requirementQuantity` as DOUBLE) as requirementQuantity,
    case when `storageLocation_externalId` is not null and trim(cast(`storageLocation_externalId` as STRING)) != ''
         then node_reference('{{ isc_InstanceSpace }}', cast(`storageLocation_externalId` as STRING))
         else null end as storageLocation,
    case when `supplyingPlant_externalId` is not null and trim(cast(`supplyingPlant_externalId` as STRING)) != ''
         then node_reference('{{ isc_InstanceSpace }}', cast(`supplyingPlant_externalId` as STRING))
         else null end as supplyingPlant,
    cast(`sourceId` as STRING) as sourceId,
    cast(`sourceContext` as STRING) as sourceContext,
    cast(`sourceCreatedTime` as STRING) as sourceCreatedTime,
    cast(`sourceUpdatedTime` as STRING) as sourceUpdatedTime,
    cast(`sourceCreatedUser` as STRING) as sourceCreatedUser,
    cast(`sourceUpdatedUser` as STRING) as sourceUpdatedUser
FROM
    `{{ btpSeedDbName }}`.`work_order_component`
