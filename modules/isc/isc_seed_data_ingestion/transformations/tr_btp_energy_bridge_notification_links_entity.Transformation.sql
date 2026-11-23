-- Transformation: tr_btp_energy_bridge_notification_links_entity
-- Source: {{ btpSeedDbName }}.notification_links_entity (RAW)
-- Target: NotificationLinksEntity (edge MasterNotification.linksEntity) ({{ isc_OrganizationalFoundationSchemaSpace }}:OrganizationalFoundation/{{dmVersion}})
-- Instance space: {{ isc_InstanceSpace }}


SELECT
    cast(`key` as STRING) as externalId,
    case when `startNotification_externalId` is not null and trim(cast(`startNotification_externalId` as STRING)) != ''
         then node_reference('{{ isc_InstanceSpace }}', cast(`startNotification_externalId` as STRING))
         else null end as startNode,
    case when `endWorkOrder_externalId` is not null and trim(cast(`endWorkOrder_externalId` as STRING)) != ''
         then node_reference('{{ isc_InstanceSpace }}', cast(`endWorkOrder_externalId` as STRING))
         else null end as endNode,
    node_reference('{{ isc_OrganizationalFoundationSchemaSpace }}', 'MasterNotification.linksEntity') as type,
    cast(`name` as STRING) as name,
    cast(`description` as STRING) as description,
    cast(`relationType` as STRING) as relationType,
    cast(`relationStatus` as STRING) as relationStatus,
    cast(`validFrom` as STRING) as validFrom,
    cast(`validTo` as STRING) as validTo,
    cast(`linkRole` as STRING) as linkRole,
    cast(`severityAtLinkTime` as STRING) as severityAtLinkTime,
    cast(`correlationId` as STRING) as correlationId,
    cast(`impactCategory` as STRING) as impactCategory,
    cast(`sourceId` as STRING) as sourceId,
    cast(`sourceContext` as STRING) as sourceContext,
    cast(`sourceCreatedTime` as STRING) as sourceCreatedTime,
    cast(`sourceUpdatedTime` as STRING) as sourceUpdatedTime,
    cast(`sourceCreatedUser` as STRING) as sourceCreatedUser,
    cast(`sourceUpdatedUser` as STRING) as sourceUpdatedUser
FROM
    `{{ btpSeedDbName }}`.`notification_links_entity`
