-- Transformation: tr_btp_energy_bridge_shipment
-- Source: {{ btpSeedDbName }}.shipment (RAW)
-- Target: Shipment ({{ isc_ShipmentDeliverySchemaSpace }}:ShipmentDelivery/{{dmVersion}})
-- Instance space: {{ isc_InstanceSpace }}


SELECT
    cast(`key` as STRING) as externalId,
    '{{ isc_InstanceSpace }}' as space,
    cast(`name` as STRING) as name,
    cast(`description` as STRING) as description,
    cast(`shipmentId` as STRING) as shipmentId,
    cast(`modeOfTransport` as STRING) as modeOfTransport,
    case when `originSite_externalId` is not null and trim(cast(`originSite_externalId` as STRING)) != ''
         then node_reference('{{ isc_InstanceSpace }}', cast(`originSite_externalId` as STRING))
         else null end as originSite,
    case when `originWarehouse_externalId` is not null and trim(cast(`originWarehouse_externalId` as STRING)) != ''
         then node_reference('{{ isc_InstanceSpace }}', cast(`originWarehouse_externalId` as STRING))
         else null end as originWarehouse,
    case when `originSupplierFacility_externalId` is not null and trim(cast(`originSupplierFacility_externalId` as STRING)) != ''
         then node_reference('{{ isc_InstanceSpace }}', cast(`originSupplierFacility_externalId` as STRING))
         else null end as originSupplierFacility,
    case when `supplier_externalId` is not null and trim(cast(`supplier_externalId` as STRING)) != ''
         then node_reference('{{ isc_InstanceSpace }}', cast(`supplier_externalId` as STRING))
         else null end as supplier,
    case when `destinationSite_externalId` is not null and trim(cast(`destinationSite_externalId` as STRING)) != ''
         then node_reference('{{ isc_InstanceSpace }}', cast(`destinationSite_externalId` as STRING))
         else null end as destinationSite,
    case when `destinationWarehouse_externalId` is not null and trim(cast(`destinationWarehouse_externalId` as STRING)) != ''
         then node_reference('{{ isc_InstanceSpace }}', cast(`destinationWarehouse_externalId` as STRING))
         else null end as destinationWarehouse,
    cast(`departureDate` as STRING) as departureDate,
    cast(`originalEstimatedArrivalDate` as STRING) as originalEstimatedArrivalDate,
    cast(`estimatedArrivalDate` as STRING) as estimatedArrivalDate,
    cast(`actualArrivalDate` as STRING) as actualArrivalDate,
    cast(`trackingNumber` as STRING) as trackingNumber,
    cast(`shipmentStatus` as STRING) as shipmentStatus,
    cast(`sourceId` as STRING) as sourceId,
    cast(`sourceContext` as STRING) as sourceContext,
    cast(`sourceCreatedTime` as STRING) as sourceCreatedTime,
    cast(`sourceUpdatedTime` as STRING) as sourceUpdatedTime,
    cast(`sourceCreatedUser` as STRING) as sourceCreatedUser,
    cast(`sourceUpdatedUser` as STRING) as sourceUpdatedUser
FROM
    `{{ btpSeedDbName }}`.`shipment`
