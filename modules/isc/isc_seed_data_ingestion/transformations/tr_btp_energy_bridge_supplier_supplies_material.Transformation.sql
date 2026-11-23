-- Transformation: tr_btp_energy_bridge_supplier_supplies_material
-- Source: {{ btpSeedDbName }}.supplier_supplies_material (RAW)
-- Target: SupplierSuppliesMaterial (edge Supplier.suppliesMaterial) ({{ isc_SourcingProcurementSchemaSpace }}:SourcingProcurement/{{dmVersion}})
-- Instance space: {{ isc_InstanceSpace }}


SELECT
    cast(`key` as STRING) as externalId,
    case when `startSupplier_externalId` is not null and trim(cast(`startSupplier_externalId` as STRING)) != ''
         then node_reference('{{ isc_InstanceSpace }}', cast(`startSupplier_externalId` as STRING))
         else null end as startNode,
    case when `endMaterial_externalId` is not null and trim(cast(`endMaterial_externalId` as STRING)) != ''
         then node_reference('{{ isc_InstanceSpace }}', cast(`endMaterial_externalId` as STRING))
         else null end as endNode,
    node_reference('{{ isc_SourcingProcurementSchemaSpace }}', 'Supplier.suppliesMaterial') as type,
    cast(`name` as STRING) as name,
    cast(`description` as STRING) as description,
    cast(`relationType` as STRING) as relationType,
    cast(`relationStatus` as STRING) as relationStatus,
    cast(`validFrom` as STRING) as validFrom,
    cast(`validTo` as STRING) as validTo,
    cast(`unitCost` as DOUBLE) as unitCost,
    cast(`currency` as STRING) as currency,
    cast(`priorityRank` as DOUBLE) as priorityRank,
    cast(`contractRef` as STRING) as contractRef,
    cast(`minQuantity` as DOUBLE) as minQuantity,
    cast(`maxQuantity` as DOUBLE) as maxQuantity,
    cast(`otifScore` as DOUBLE) as otifScore,
    cast(`otifScorePeriodStart` as STRING) as otifScorePeriodStart,
    cast(`otifScorePeriodEnd` as STRING) as otifScorePeriodEnd
FROM
    `{{ btpSeedDbName }}`.`supplier_supplies_material`
