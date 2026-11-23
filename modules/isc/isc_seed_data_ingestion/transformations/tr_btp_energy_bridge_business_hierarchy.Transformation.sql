-- Transformation: tr_btp_energy_bridge_business_hierarchy
-- Source: {{ btpSeedDbName }}.business_hierarchy (RAW)
-- Target: BusinessUnits ({{ isc_OrganizationalFoundationSchemaSpace }}:OrganizationalFoundation/{{dmVersion}})
-- Instance space: {{ isc_InstanceSpace }}
-- declaredType points at the DeclaredTypes node named after the concrete view (Company/BusinessUnit/CostCenter).

SELECT
    cast(`key` as STRING) as externalId,
    '{{ isc_InstanceSpace }}' as space,
    cast(`name` as STRING) as name,
    cast(`description` as STRING) as description,
    cast(`hierarchyCode` as STRING) as hierarchyCode,
    case when `parent_externalId` is not null and trim(cast(`parent_externalId` as STRING)) != ''
         then node_reference('{{ isc_InstanceSpace }}', cast(`parent_externalId` as STRING))
         else null end as parent,
    cast(`companyCode` as STRING) as companyCode,
    cast(`currency` as STRING) as currency,
    cast(`sourceId` as STRING) as sourceId,
    cast(`sourceContext` as STRING) as sourceContext,
    cast(`sourceCreatedTime` as STRING) as sourceCreatedTime,
    cast(`sourceUpdatedTime` as STRING) as sourceUpdatedTime,
    cast(`sourceCreatedUser` as STRING) as sourceCreatedUser,
    cast(`sourceUpdatedUser` as STRING) as sourceUpdatedUser,
    cast(`costCenter` as STRING) as costCenter,
    case when `hierarchyType` in ('Company', 'BusinessUnit', 'CostCenter')
         then node_reference('{{ isc_OrganizationalFoundationSchemaSpace }}', cast(`hierarchyType` as STRING))
         else null end as declaredType
FROM
    `{{ btpSeedDbName }}`.`business_hierarchy`
