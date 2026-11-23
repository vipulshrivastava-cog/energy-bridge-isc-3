-- Transformation: tr_btp_energy_bridge_work_order
-- Source: {{ btpSeedDbName }}.work_order (RAW)
-- Target: WorkOrder ({{ isc_AssetMaintenanceSchemaSpace }}:AssetMaintenance/{{dmVersion}})
-- Instance space: {{ isc_InstanceSpace }}
-- Inherited CogniteActivity timestamps (scheduledStartTime, ...) also satisfy requires(CogniteSchedulable).

SELECT
    cast(`key` as STRING) as externalId,
    '{{ isc_InstanceSpace }}' as space,
    cast(`name` as STRING) as name,
    cast(`description` as STRING) as description,
    cast(`workOrderId` as STRING) as workOrderId,
    cast(`workOrderNumber` as STRING) as workOrderNumber,
    cast(`workOrderStatus` as STRING) as workOrderStatus,
    cast(`priority` as BIGINT) as priority,
    case when `aboutFunctionalLocation_externalId` is not null and trim(cast(`aboutFunctionalLocation_externalId` as STRING)) != ''
         then node_reference('{{ isc_InstanceSpace }}', cast(`aboutFunctionalLocation_externalId` as STRING))
         else null end as aboutFunctionalLocation,
    case when `planningPlant_externalId` is not null and trim(cast(`planningPlant_externalId` as STRING)) != ''
         then node_reference('{{ isc_InstanceSpace }}', cast(`planningPlant_externalId` as STRING))
         else null end as planningPlant,
    case when `executionPlant_externalId` is not null and trim(cast(`executionPlant_externalId` as STRING)) != ''
         then node_reference('{{ isc_InstanceSpace }}', cast(`executionPlant_externalId` as STRING))
         else null end as executionPlant,
    cast(`equipmentNumber` as STRING) as equipmentNumber,
    cast(`equipmentDescription` as STRING) as equipmentDescription,
    cast(`workCenter` as STRING) as workCenter,
    cast(`costCenter` as STRING) as costCenter,
    cast(`currency` as STRING) as currency,
    cast(`scheduledStartTime` as STRING) as scheduledStartTime,
    cast(`scheduledEndTime` as STRING) as scheduledEndTime,
    cast(`startTime` as STRING) as startTime,
    cast(`endTime` as STRING) as endTime,
    cast(`basicStartDate` as STRING) as basicStartDate,
    cast(`basicFinishDate` as STRING) as basicFinishDate,
    cast(`workOrderMaterialStatus` as STRING) as workOrderMaterialStatus,
    cast(`overallMaterialStatus` as STRING) as overallMaterialStatus,
    cast(`isSafetyCritical` as BOOLEAN) as isSafetyCritical,
    cast(`sourceId` as STRING) as sourceId,
    cast(`sourceContext` as STRING) as sourceContext,
    cast(`sourceCreatedTime` as STRING) as sourceCreatedTime,
    cast(`sourceUpdatedTime` as STRING) as sourceUpdatedTime,
    cast(`sourceCreatedUser` as STRING) as sourceCreatedUser,
    cast(`sourceUpdatedUser` as STRING) as sourceUpdatedUser,
    cast(`previousScheduledStartTime` as STRING) as previousScheduledStartTime
FROM
    `{{ btpSeedDbName }}`.`work_order`
