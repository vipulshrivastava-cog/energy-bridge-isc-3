-- Transformation: tr_btp_energy_bridge_uses_transportation_lane
-- Source: {{ btpSeedDbName }}.uses_transportation_lane (RAW)
-- Target: UsesTransportationLane (edge Shipment.usesTransportationLane) ({{ isc_ShipmentDeliverySchemaSpace }}:ShipmentDelivery/{{dmVersion}})
-- Instance space: {{ isc_InstanceSpace }}


SELECT
    cast(`key` as STRING) as externalId,
    case when `startShipment_externalId` is not null and trim(cast(`startShipment_externalId` as STRING)) != ''
         then node_reference('{{ isc_InstanceSpace }}', cast(`startShipment_externalId` as STRING))
         else null end as startNode,
    case when `endLane_externalId` is not null and trim(cast(`endLane_externalId` as STRING)) != ''
         then node_reference('{{ isc_InstanceSpace }}', cast(`endLane_externalId` as STRING))
         else null end as endNode,
    node_reference('{{ isc_ShipmentDeliverySchemaSpace }}', 'Shipment.usesTransportationLane') as type,
    cast(`name` as STRING) as name,
    cast(`description` as STRING) as description,
    cast(`relationType` as STRING) as relationType,
    cast(`relationStatus` as STRING) as relationStatus,
    cast(`validFrom` as STRING) as validFrom,
    cast(`validTo` as STRING) as validTo,
    cast(`plannedTransitDays` as DOUBLE) as plannedTransitDays,
    cast(`actualTransitDays` as DOUBLE) as actualTransitDays,
    cast(`delayReason` as STRING) as delayReason,
    cast(`actualCost` as DOUBLE) as actualCost,
    cast(`costCurrency` as STRING) as costCurrency,
    cast(`customsClearanceRequired` as BOOLEAN) as customsClearanceRequired,
    cast(`legSequence` as INT) as legSequence,
    cast(`legRole` as STRING) as legRole
FROM
    `{{ btpSeedDbName }}`.`uses_transportation_lane`
