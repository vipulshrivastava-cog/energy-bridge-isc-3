-- Transformation: tr_btp_energy_bridge_geo_location
-- Source: {{ btpSeedDbName }}.geo_location (RAW)
-- Target: GeoLocations ({{ isc_OrganizationalFoundationSchemaSpace }}:OrganizationalFoundation/{{dmVersion}})
-- Instance space: {{ isc_InstanceSpace }}
-- declaredType points at the DeclaredTypes node named after the concrete view (GeoRegion/Country/City).

SELECT
    cast(`key` as STRING) as externalId,
    '{{ isc_InstanceSpace }}' as space,
    cast(`name` as STRING) as name,
    cast(`description` as STRING) as description,
    cast(`locationCode` as STRING) as locationCode,
    case when `parent_externalId` is not null and trim(cast(`parent_externalId` as STRING)) != ''
         then node_reference('{{ isc_InstanceSpace }}', cast(`parent_externalId` as STRING))
         else null end as parent,
    cast(`isoCode` as STRING) as isoCode,
    cast(`sourceId` as STRING) as sourceId,
    cast(`sourceContext` as STRING) as sourceContext,
    cast(`sourceCreatedTime` as STRING) as sourceCreatedTime,
    cast(`sourceUpdatedTime` as STRING) as sourceUpdatedTime,
    cast(`sourceCreatedUser` as STRING) as sourceCreatedUser,
    cast(`sourceUpdatedUser` as STRING) as sourceUpdatedUser,
    cast(`latitude` as DOUBLE) as latitude,
    cast(`longitude` as DOUBLE) as longitude,
    cast(`physicalAddress` as STRING) as physicalAddress,
    case when `locationType` in ('GeoRegion', 'Country', 'City')
         then node_reference('{{ isc_OrganizationalFoundationSchemaSpace }}', cast(`locationType` as STRING))
         else null end as declaredType
FROM
    `{{ btpSeedDbName }}`.`geo_location`
