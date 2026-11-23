-- Transformation: tr_btp_energy_bridge_material_reservation
-- Source: {{ btpSeedDbName }}.material_reservation (RAW)
-- Target: MaterialReservation (edge MaterialInventory.reservedForWorkOrderComponent) ({{ isc_MaterialManagementSchemaSpace }}:MaterialManagement/{{dmVersion}})
-- Instance space: {{ isc_InstanceSpace }}


SELECT
    cast(`key` as STRING) as externalId,
    case when `startMaterialInventory_externalId` is not null and trim(cast(`startMaterialInventory_externalId` as STRING)) != ''
         then node_reference('{{ isc_InstanceSpace }}', cast(`startMaterialInventory_externalId` as STRING))
         else null end as startNode,
    case when `target_externalId` is not null and trim(cast(`target_externalId` as STRING)) != ''
         then node_reference('{{ isc_InstanceSpace }}', cast(`target_externalId` as STRING))
         else null end as endNode,
    node_reference('{{ isc_MaterialManagementSchemaSpace }}', 'MaterialInventory.reservedForWorkOrderComponent') as type,
    cast(`name` as STRING) as name,
    cast(`description` as STRING) as description,
    cast(`reservationNumber` as STRING) as reservationNumber,
    cast(`quantityReserved` as DOUBLE) as quantityReserved,
    cast(`reservationDate` as STRING) as reservationDate,
    cast(`requirementDate` as STRING) as requirementDate,
    cast(`relationType` as STRING) as relationType,
    cast(`relationStatus` as STRING) as relationStatus,
    cast(`validFrom` as STRING) as validFrom,
    cast(`validTo` as STRING) as validTo,
    cast(`sourceSystem` as STRING) as sourceSystem,
    cast(`linkLastUpdatedTime` as STRING) as linkLastUpdatedTime,
    cast(`quantityUnit` as STRING) as quantityUnit
FROM
    `{{ btpSeedDbName }}`.`material_reservation`
