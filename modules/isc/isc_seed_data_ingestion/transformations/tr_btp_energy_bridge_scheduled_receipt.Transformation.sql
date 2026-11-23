-- Transformation: tr_btp_energy_bridge_scheduled_receipt
-- Source: {{ btpSeedDbName }}.scheduled_receipt (RAW)
-- Target: ScheduledReceipt ({{ isc_ShipmentDeliverySchemaSpace }}:ShipmentDelivery/{{dmVersion}})
-- Instance space: {{ isc_InstanceSpace }}


SELECT
    cast(`key` as STRING) as externalId,
    '{{ isc_InstanceSpace }}' as space,
    cast(`name` as STRING) as name,
    cast(`description` as STRING) as description,
    cast(`scheduledReceiptId` as STRING) as scheduledReceiptId,
    cast(`scheduledReceiptLineNumber` as STRING) as scheduledReceiptLineNumber,
    cast(`deliveryType` as STRING) as deliveryType,
    cast(`scheduledQuantity` as DOUBLE) as scheduledQuantity,
    case when `originCountry_externalId` is not null and trim(cast(`originCountry_externalId` as STRING)) != ''
         then node_reference('{{ isc_InstanceSpace }}', cast(`originCountry_externalId` as STRING))
         else null end as originCountry,
    case when `originSupplierSite_externalId` is not null and trim(cast(`originSupplierSite_externalId` as STRING)) != ''
         then node_reference('{{ isc_InstanceSpace }}', cast(`originSupplierSite_externalId` as STRING))
         else null end as originSupplierSite,
    case when `destinationCountry_externalId` is not null and trim(cast(`destinationCountry_externalId` as STRING)) != ''
         then node_reference('{{ isc_InstanceSpace }}', cast(`destinationCountry_externalId` as STRING))
         else null end as destinationCountry,
    case when `destinationSite_externalId` is not null and trim(cast(`destinationSite_externalId` as STRING)) != ''
         then node_reference('{{ isc_InstanceSpace }}', cast(`destinationSite_externalId` as STRING))
         else null end as destinationSite,
    case when `destinationWarehouse_externalId` is not null and trim(cast(`destinationWarehouse_externalId` as STRING)) != ''
         then node_reference('{{ isc_InstanceSpace }}', cast(`destinationWarehouse_externalId` as STRING))
         else null end as destinationWarehouse,
    cast(`scheduledPickupDate` as STRING) as scheduledPickupDate,
    cast(`scheduledArrivalDate` as STRING) as scheduledArrivalDate,
    cast(`scheduleStatus` as STRING) as scheduleStatus,
    case when `material_externalId` is not null and trim(cast(`material_externalId` as STRING)) != ''
         then node_reference('{{ isc_InstanceSpace }}', cast(`material_externalId` as STRING))
         else null end as material,
    case when `poLineItem_externalId` is not null and trim(cast(`poLineItem_externalId` as STRING)) != ''
         then node_reference('{{ isc_InstanceSpace }}', cast(`poLineItem_externalId` as STRING))
         else null end as poLineItem,
    cast(`quantityUnit` as STRING) as quantityUnit,
    case when `supplier_externalId` is not null and trim(cast(`supplier_externalId` as STRING)) != ''
         then node_reference('{{ isc_InstanceSpace }}', cast(`supplier_externalId` as STRING))
         else null end as supplier,
    case when `poConfirmation_externalId` is not null and trim(cast(`poConfirmation_externalId` as STRING)) != ''
         then node_reference('{{ isc_InstanceSpace }}', cast(`poConfirmation_externalId` as STRING))
         else null end as poConfirmation,
    case when `transportationLane_externalId` is not null and trim(cast(`transportationLane_externalId` as STRING)) != ''
         then node_reference('{{ isc_InstanceSpace }}', cast(`transportationLane_externalId` as STRING))
         else null end as transportationLane,
    cast(`plannedTransitDays` as DOUBLE) as plannedTransitDays,
    cast(`originalArrivalDate` as STRING) as originalArrivalDate,
    cast(`revisedArrivalDate` as STRING) as revisedArrivalDate,
    cast(`delayReason` as STRING) as delayReason,
    cast(`sourceId` as STRING) as sourceId,
    cast(`sourceContext` as STRING) as sourceContext,
    cast(`sourceCreatedTime` as STRING) as sourceCreatedTime,
    cast(`sourceUpdatedTime` as STRING) as sourceUpdatedTime,
    cast(`sourceCreatedUser` as STRING) as sourceCreatedUser,
    cast(`sourceUpdatedUser` as STRING) as sourceUpdatedUser
FROM
    `{{ btpSeedDbName }}`.`scheduled_receipt`
