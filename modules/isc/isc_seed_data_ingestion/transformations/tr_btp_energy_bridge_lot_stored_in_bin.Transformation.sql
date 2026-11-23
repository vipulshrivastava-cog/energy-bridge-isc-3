-- Transformation: tr_btp_energy_bridge_lot_stored_in_bin
-- Source: {{ btpSeedDbName }}.lot_stored_in_bin (RAW)
-- Target: LotStoredInBin (edge MaterialLot.storedInBin) ({{ isc_MaterialManagementSchemaSpace }}:MaterialManagement/{{dmVersion}})
-- Instance space: {{ isc_InstanceSpace }}


SELECT
    cast(`key` as STRING) as externalId,
    case when `materialLot_externalId` is not null and trim(cast(`materialLot_externalId` as STRING)) != ''
         then node_reference('{{ isc_InstanceSpace }}', cast(`materialLot_externalId` as STRING))
         else null end as startNode,
    case when `storageBin_externalId` is not null and trim(cast(`storageBin_externalId` as STRING)) != ''
         then node_reference('{{ isc_InstanceSpace }}', cast(`storageBin_externalId` as STRING))
         else null end as endNode,
    node_reference('{{ isc_MaterialManagementSchemaSpace }}', 'MaterialLot.storedInBin') as type,
    cast(`qtyOnHand` as DOUBLE) as qtyOnHand,
    cast(`lastUpdated` as STRING) as lastUpdated,
    cast(`relationType` as STRING) as relationType,
    cast(`relationStatus` as STRING) as relationStatus,
    cast(`validFrom` as STRING) as validFrom,
    cast(`validTo` as STRING) as validTo,
    cast(`sourceSystem` as STRING) as sourceSystem,
    cast(`linkLastUpdatedTime` as STRING) as linkLastUpdatedTime,
    cast(`sourceId` as STRING) as sourceId,
    cast(`sourceContext` as STRING) as sourceContext,
    cast(`sourceCreatedTime` as STRING) as sourceCreatedTime,
    cast(`sourceUpdatedTime` as STRING) as sourceUpdatedTime,
    cast(`sourceCreatedUser` as STRING) as sourceCreatedUser,
    cast(`sourceUpdatedUser` as STRING) as sourceUpdatedUser
FROM
    `{{ btpSeedDbName }}`.`lot_stored_in_bin`
