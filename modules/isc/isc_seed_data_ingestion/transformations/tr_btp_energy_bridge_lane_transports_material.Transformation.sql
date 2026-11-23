-- Transformation: tr_btp_energy_bridge_lane_transports_material
-- Source: {{ btpSeedDbName }}.lane_transports_material (RAW)
-- Target: LaneTransportsMaterial (edge TransportationLane.transportsMaterial) ({{ isc_ShipmentDeliverySchemaSpace }}:ShipmentDelivery/{{dmVersion}})
-- Instance space: {{ isc_InstanceSpace }}


SELECT
    cast(`key` as STRING) as externalId,
    case when `startLane_externalId` is not null and trim(cast(`startLane_externalId` as STRING)) != ''
         then node_reference('{{ isc_InstanceSpace }}', cast(`startLane_externalId` as STRING))
         else null end as startNode,
    case when `endMaterial_externalId` is not null and trim(cast(`endMaterial_externalId` as STRING)) != ''
         then node_reference('{{ isc_InstanceSpace }}', cast(`endMaterial_externalId` as STRING))
         else null end as endNode,
    node_reference('{{ isc_ShipmentDeliverySchemaSpace }}', 'TransportationLane.transportsMaterial') as type,
    cast(`name` as STRING) as name,
    cast(`description` as STRING) as description,
    cast(`relationType` as STRING) as relationType,
    cast(`relationStatus` as STRING) as relationStatus,
    cast(`validFrom` as STRING) as validFrom,
    cast(`validTo` as STRING) as validTo,
    cast(`priorityRank` as DOUBLE) as priorityRank,
    cast(`minLotSize` as DOUBLE) as minLotSize,
    cast(`maxLotSize` as DOUBLE) as maxLotSize,
    cast(`lotSizeUnit` as STRING) as lotSizeUnit,
    cast(`costPerTonne` as DOUBLE) as costPerTonne,
    cast(`costCurrency` as STRING) as costCurrency,
    cast(`hazardousGoodsApproved` as BOOLEAN) as hazardousGoodsApproved,
    cast(`customsClearanceRequired` as BOOLEAN) as customsClearanceRequired
FROM
    `{{ btpSeedDbName }}`.`lane_transports_material`
