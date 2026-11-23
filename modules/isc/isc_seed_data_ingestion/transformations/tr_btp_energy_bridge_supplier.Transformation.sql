-- Transformation: tr_btp_energy_bridge_supplier
-- Source: {{ btpSeedDbName }}.supplier (RAW)
-- Target: Supplier ({{ isc_SourcingProcurementSchemaSpace }}:SourcingProcurement/{{dmVersion}})
-- Instance space: {{ isc_InstanceSpace }}


SELECT
    cast(`key` as STRING) as externalId,
    '{{ isc_InstanceSpace }}' as space,
    cast(`name` as STRING) as name,
    cast(`description` as STRING) as description,
    cast(`supplierId` as STRING) as supplierId,
    cast(`certificationStatus` as STRING) as certificationStatus,
    cast(`performanceRating` as DOUBLE) as performanceRating,
    cast(`supplierCountry` as STRING) as supplierCountry,
    cast(`supplierRiskRating` as STRING) as supplierRiskRating,
    cast(`businessValuePriority` as STRING) as businessValuePriority,
    cast(`sourceId` as STRING) as sourceId,
    cast(`sourceContext` as STRING) as sourceContext,
    cast(`sourceCreatedTime` as STRING) as sourceCreatedTime,
    cast(`sourceUpdatedTime` as STRING) as sourceUpdatedTime,
    cast(`sourceCreatedUser` as STRING) as sourceCreatedUser,
    cast(`sourceUpdatedUser` as STRING) as sourceUpdatedUser
FROM
    `{{ btpSeedDbName }}`.`supplier`
