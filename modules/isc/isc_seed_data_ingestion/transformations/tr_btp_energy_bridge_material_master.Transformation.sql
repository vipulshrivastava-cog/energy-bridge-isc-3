-- Transformation: tr_btp_energy_bridge_material_master
-- Source: {{ btpSeedDbName }}.material_master (RAW)
-- Target: MaterialMaster ({{ isc_MaterialManagementSchemaSpace }}:MaterialManagement/{{dmVersion}})
-- Instance space: {{ isc_InstanceSpace }}


SELECT
    cast(`key` as STRING) as externalId,
    '{{ isc_InstanceSpace }}' as space,
    cast(`name` as STRING) as name,
    cast(`description` as STRING) as description,
    cast(`materialId` as STRING) as materialId,
    cast(`materialType` as STRING) as materialType,
    cast(`baseUnitOfMeasure` as STRING) as baseUnitOfMeasure,
    cast(`sourceId` as STRING) as sourceId,
    cast(`sourceContext` as STRING) as sourceContext,
    cast(`sourceCreatedTime` as STRING) as sourceCreatedTime,
    cast(`sourceUpdatedTime` as STRING) as sourceUpdatedTime,
    cast(`sourceCreatedUser` as STRING) as sourceCreatedUser,
    cast(`sourceUpdatedUser` as STRING) as sourceUpdatedUser,
    cast(`isCriticalSpare` as BOOLEAN) as isCriticalSpare,
    cast(`criticalityRating` as STRING) as criticalityRating,
    cast(`abcIndicator` as STRING) as abcIndicator,
    cast(`stdCost` as DOUBLE) as stdCost,
    cast(`priceControlIndicator` as STRING) as priceControlIndicator
FROM
    `{{ btpSeedDbName }}`.`material_master`
