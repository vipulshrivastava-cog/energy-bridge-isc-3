-- Transformation: tr_btp_energy_bridge_forecast
-- Source: {{ btpSeedDbName }}.forecast (RAW)
-- Target: Forecast ({{ isc_PlanForecastSchemaSpace }}:PlanForecast/{{dmVersion}})
-- Instance space: {{ isc_InstanceSpace }}


SELECT
    cast(`key` as STRING) as externalId,
    '{{ isc_InstanceSpace }}' as space,
    cast(`name` as STRING) as name,
    cast(`description` as STRING) as description,
    cast(`forecastId` as STRING) as forecastId,
    cast(`forecastType` as STRING) as forecastType,
    cast(`forecastSource` as STRING) as forecastSource,
    cast(`forecastVersion` as STRING) as forecastVersion,
    cast(`forecastStatus` as STRING) as forecastStatus,
    case when `material_externalId` is not null and trim(cast(`material_externalId` as STRING)) != ''
         then node_reference('{{ isc_InstanceSpace }}', cast(`material_externalId` as STRING))
         else null end as material,
    case when `plant_externalId` is not null and trim(cast(`plant_externalId` as STRING)) != ''
         then node_reference('{{ isc_InstanceSpace }}', cast(`plant_externalId` as STRING))
         else null end as plant,
    cast(`timeBucket` as STRING) as timeBucket,
    cast(`forecastPeriodStart` as STRING) as forecastPeriodStart,
    cast(`forecastPeriodEnd` as STRING) as forecastPeriodEnd,
    cast(`forecastHorizonEnd` as STRING) as forecastHorizonEnd,
    cast(`forecastQuantity` as DOUBLE) as forecastQuantity,
    cast(`adjustedQuantity` as DOUBLE) as adjustedQuantity,
    cast(`unitOfMeasure` as STRING) as unitOfMeasure,
    cast(`confidence` as DOUBLE) as confidence,
    cast(`priceIndexName` as STRING) as priceIndexName,
    case when `workOrder_externalId` is not null and trim(cast(`workOrder_externalId` as STRING)) != ''
         then node_reference('{{ isc_InstanceSpace }}', cast(`workOrder_externalId` as STRING))
         else null end as workOrder,
    cast(`sourceId` as STRING) as sourceId,
    cast(`sourceContext` as STRING) as sourceContext,
    cast(`sourceCreatedTime` as STRING) as sourceCreatedTime,
    cast(`sourceUpdatedTime` as STRING) as sourceUpdatedTime,
    cast(`sourceCreatedUser` as STRING) as sourceCreatedUser,
    cast(`sourceUpdatedUser` as STRING) as sourceUpdatedUser
FROM
    `{{ btpSeedDbName }}`.`forecast`
