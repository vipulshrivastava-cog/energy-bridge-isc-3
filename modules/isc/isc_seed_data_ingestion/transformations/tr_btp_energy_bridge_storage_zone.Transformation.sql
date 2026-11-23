-- Transformation: tr_btp_energy_bridge_storage_zone
-- Source: {{ btpSeedDbName }}.storage_location_node (RAW)
-- Target: Zone ({{ isc_TypedModelSchemaSpace }}:isc_typed_model/{{dmVersion}})
-- Instance space: {{ isc_InstanceSpace }}


SELECT
    cast(`key` as STRING) as externalId,
    '{{ isc_InstanceSpace }}' as space,
    cast(`name` as STRING) as name,
    cast(`description` as STRING) as description,
    cast(`hierarchyCode` as STRING) as hierarchyCode,
    case when `parent_externalId` is not null and trim(cast(`parent_externalId` as STRING)) != ''
         then node_reference('{{ isc_InstanceSpace }}', cast(`parent_externalId` as STRING))
         else null end as warehouse,
    cast(`sourceId` as STRING) as sourceId,
    cast(`sourceContext` as STRING) as sourceContext,
    cast(`sourceCreatedTime` as STRING) as sourceCreatedTime,
    cast(`sourceUpdatedTime` as STRING) as sourceUpdatedTime,
    cast(`sourceCreatedUser` as STRING) as sourceCreatedUser,
    cast(`sourceUpdatedUser` as STRING) as sourceUpdatedUser,
    node_reference('{{ isc_OrganizationalFoundationSchemaSpace }}', 'Zone') as declaredType
FROM
    `{{ btpSeedDbName }}`.`storage_location_node`
WHERE `hierarchyType` = 'Zone'
