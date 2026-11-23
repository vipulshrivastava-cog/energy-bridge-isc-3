-- Transformation: tr_btp_energy_bridge_supplier_facility
-- Source: {{ btpSeedDbName }}.supplier_facility (RAW)
-- Target: SupplierFacility ({{ isc_SourcingProcurementSchemaSpace }}:SourcingProcurement/{{dmVersion}})
-- Instance space: {{ isc_InstanceSpace }}


SELECT
    cast(`key` as STRING) as externalId,
    '{{ isc_InstanceSpace }}' as space,
    cast(`name` as STRING) as name,
    cast(`description` as STRING) as description,
    cast(`siteCode` as STRING) as siteCode,
    cast(`siteType` as STRING) as siteType,
    case when `supplier_externalId` is not null and trim(cast(`supplier_externalId` as STRING)) != ''
         then node_reference('{{ isc_InstanceSpace }}', cast(`supplier_externalId` as STRING))
         else null end as supplier,
    case when `geoLocation_externalId` is not null and trim(cast(`geoLocation_externalId` as STRING)) != ''
         then node_reference('{{ isc_InstanceSpace }}', cast(`geoLocation_externalId` as STRING))
         else null end as geoLocation,
    cast(`locationCity` as STRING) as locationCity,
    cast(`physicalAddress` as STRING) as physicalAddress,
    cast(`latitude` as DOUBLE) as latitude,
    cast(`longitude` as DOUBLE) as longitude,
    cast(`contactName` as STRING) as contactName,
    cast(`contactEmail` as STRING) as contactEmail,
    cast(`contactPhone` as STRING) as contactPhone,
    cast(`taxId` as STRING) as taxId,
    cast(`paymentTerms` as STRING) as paymentTerms,
    cast(`incoterms` as STRING) as incoterms,
    cast(`orderCurrency` as STRING) as orderCurrency,
    cast(`isHeadquarters` as BOOLEAN) as isHeadquarters,
    cast(`isActive` as BOOLEAN) as isActive,
    cast(`sourceId` as STRING) as sourceId,
    cast(`sourceContext` as STRING) as sourceContext,
    cast(`sourceCreatedTime` as STRING) as sourceCreatedTime,
    cast(`sourceUpdatedTime` as STRING) as sourceUpdatedTime,
    cast(`sourceCreatedUser` as STRING) as sourceCreatedUser,
    cast(`sourceUpdatedUser` as STRING) as sourceUpdatedUser
FROM
    `{{ btpSeedDbName }}`.`supplier_facility`
