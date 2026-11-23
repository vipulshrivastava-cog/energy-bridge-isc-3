-- Transformation: tr_btp_energy_bridge_material_lot
-- Source: {{ btpSeedDbName }}.material_lot (RAW)
-- Target: MaterialLot ({{ isc_MaterialManagementSchemaSpace }}:MaterialManagement/{{dmVersion}})
-- Instance space: {{ isc_InstanceSpace }}


SELECT
    cast(`key` as STRING) as externalId,
    '{{ isc_InstanceSpace }}' as space,
    cast(`name` as STRING) as name,
    cast(`description` as STRING) as description,
    cast(`materialLotId` as STRING) as materialLotId,
    case when `material_externalId` is not null and trim(cast(`material_externalId` as STRING)) != ''
         then node_reference('{{ isc_InstanceSpace }}', cast(`material_externalId` as STRING))
         else null end as material,
    cast(`lot_number` as STRING) as lotNumber,
    cast(`sourceId` as STRING) as sourceId,
    cast(`sourceContext` as STRING) as sourceContext,
    cast(`sourceCreatedTime` as STRING) as sourceCreatedTime,
    cast(`sourceUpdatedTime` as STRING) as sourceUpdatedTime,
    cast(`sourceCreatedUser` as STRING) as sourceCreatedUser,
    cast(`sourceUpdatedUser` as STRING) as sourceUpdatedUser,
    cast(`manufactureDate` as STRING) as manufactureDate
FROM
    `{{ btpSeedDbName }}`.`material_lot`
