-- Transformation: tr_btp_energy_bridge_material_inventory
-- Source: {{ btpSeedDbName }}.material_inventory (RAW)
-- Target: MaterialInventory ({{ isc_MaterialManagementSchemaSpace }}:MaterialManagement/{{dmVersion}})
-- Instance space: {{ isc_InstanceSpace }}


SELECT
    cast(`key` as STRING) as externalId,
    '{{ isc_InstanceSpace }}' as space,
    cast(`name` as STRING) as name,
    case when `material_externalId` is not null and trim(cast(`material_externalId` as STRING)) != ''
         then node_reference('{{ isc_InstanceSpace }}', cast(`material_externalId` as STRING))
         else null end as materialId,
    case when `warehouse_externalId` is not null and trim(cast(`warehouse_externalId` as STRING)) != ''
         then node_reference('{{ isc_InstanceSpace }}', cast(`warehouse_externalId` as STRING))
         else null end as warehouse,
    cast(`qtyOnHand` as DOUBLE) as qtyOnHand,
    cast(`safetyStock` as DOUBLE) as safetyStock,
    cast(`reorderPoint` as DOUBLE) as reorderPoint,
    cast(`unitOfMeasure` as STRING) as unitOfMeasure,
    cast(`availabilityOnshore` as STRING) as availabilityOnshore,
    cast(`availabilityOffshore` as STRING) as availabilityOffshore,
    cast(`sourceId` as STRING) as sourceId,
    cast(`sourceContext` as STRING) as sourceContext,
    cast(`sourceCreatedTime` as STRING) as sourceCreatedTime,
    cast(`sourceUpdatedTime` as STRING) as sourceUpdatedTime,
    cast(`sourceCreatedUser` as STRING) as sourceCreatedUser,
    cast(`sourceUpdatedUser` as STRING) as sourceUpdatedUser,
    cast(`lastMovementDate` as STRING) as lastMovementDate
FROM
    `{{ btpSeedDbName }}`.`material_inventory`
