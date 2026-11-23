-- Transformation: tr_btp_energy_bridge_master_notification
-- Source: {{ btpSeedDbName }}.master_notification (RAW)
-- Target: MasterNotification ({{ isc_OrganizationalFoundationSchemaSpace }}:OrganizationalFoundation/{{dmVersion}})
-- Instance space: {{ isc_InstanceSpace }}


SELECT
    cast(`key` as STRING) as externalId,
    '{{ isc_InstanceSpace }}' as space,
    cast(`notificationId` as STRING) as notificationId,
    cast(`eventType` as STRING) as eventType,
    cast(`eventTimestamp` as STRING) as eventTimestamp,
    cast(`eventPriority` as STRING) as eventPriority,
    cast(`notificationCategory` as STRING) as notificationCategory,
    cast(`changeDescription` as STRING) as changeDescription,
    cast(`previousState` as STRING) as previousState,
    cast(`currentState` as STRING) as currentState,
    cast(`resolutionStatus` as STRING) as resolutionStatus,
    cast(`resolutionDate` as STRING) as resolutionDate,
    cast(`resolutionNote` as STRING) as resolutionNote,
    cast(`assignedTo` as STRING) as assignedTo,
    cast(`acknowledgedBy` as STRING) as acknowledgedBy,
    cast(`acknowledgedDate` as STRING) as acknowledgedDate,
    cast(`estimatedImpactValue` as DOUBLE) as estimatedImpactValue,
    cast(`impactCurrency` as STRING) as impactCurrency,
    cast(`sourceId` as STRING) as sourceId,
    cast(`sourceContext` as STRING) as sourceContext,
    cast(`sourceCreatedTime` as STRING) as sourceCreatedTime
FROM
    `{{ btpSeedDbName }}`.`master_notification`
