-- Transformation: tr_btp_energy_bridge_transportation_lane
-- Source: {{ btpSeedDbName }}.transportation_lane (RAW)
-- Target: TransportationLane ({{ isc_ShipmentDeliverySchemaSpace }}:ShipmentDelivery/{{dmVersion}})
-- Instance space: {{ isc_InstanceSpace }}


SELECT
    cast(`key` as STRING) as externalId,
    '{{ isc_InstanceSpace }}' as space,
    case when `originWarehouse_externalId` is not null and trim(cast(`originWarehouse_externalId` as STRING)) != ''
         then node_reference('{{ isc_InstanceSpace }}', cast(`originWarehouse_externalId` as STRING))
         else null end as originWarehouse,
    case when `originSupplierFacility_externalId` is not null and trim(cast(`originSupplierFacility_externalId` as STRING)) != ''
         then node_reference('{{ isc_InstanceSpace }}', cast(`originSupplierFacility_externalId` as STRING))
         else null end as originSupplierFacility,
    case when `destinationWarehouse_externalId` is not null and trim(cast(`destinationWarehouse_externalId` as STRING)) != ''
         then node_reference('{{ isc_InstanceSpace }}', cast(`destinationWarehouse_externalId` as STRING))
         else null end as destinationWarehouse,
    cast(`name` as STRING) as name,
    cast(`description` as STRING) as description,
    cast(`laneId` as STRING) as laneId,
    cast(`modeOfTransport` as STRING) as modeOfTransport,
    cast(`laneType` as STRING) as laneType,
    cast(`originType` as STRING) as originType,
    cast(`destinationType` as STRING) as destinationType,
    cast(`leadTime` as DOUBLE) as leadTime,
    cast(`leadTimeUnit` as STRING) as leadTimeUnit,
    cast(`laneStatus` as STRING) as laneStatus,
    cast(`isPrimary` as BOOLEAN) as isPrimary,
    cast(`validFromDate` as STRING) as validFromDate,
    cast(`validToDate` as STRING) as validToDate,
    cast(`sourceId` as STRING) as sourceId,
    cast(`sourceContext` as STRING) as sourceContext,
    cast(`sourceCreatedTime` as STRING) as sourceCreatedTime,
    cast(`sourceUpdatedTime` as STRING) as sourceUpdatedTime,
    cast(`sourceCreatedUser` as STRING) as sourceCreatedUser,
    cast(`sourceUpdatedUser` as STRING) as sourceUpdatedUser
FROM
    `{{ btpSeedDbName }}`.`transportation_lane`
