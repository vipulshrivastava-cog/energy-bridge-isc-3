-- Transformation: tr_btp_energy_bridge_functional_asset_parent
-- Source: {{ btpSeedDbName }}.functional_asset (RAW)
-- Target: FunctionalAsset ({{ isc_AssetMaintenanceSchemaSpace }}:AssetMaintenance/{{dmVersion}})
-- Instance space: {{ isc_InstanceSpace }}
-- Pass 2: set `parent` when the parent node already exists; repeats pass-1 scalars so every upsert is complete.

SELECT
    cast(t.`key` as STRING) as externalId,
    '{{ isc_InstanceSpace }}' as space,
    cast(t.`functionalAssetLevel` as STRING) as functionalAssetLevel,
    cast(t.`erp_id` as STRING) as erp_id,
    cast(t.`assetCriticality` as DOUBLE) as assetCriticality,
    cast(t.`assetCriticalityDescription` as STRING) as assetCriticalityDescription,
    cast(t.`assetHealthScore` as DOUBLE) as assetHealthScore,
    cast(t.`assetHealthScoreDescription` as STRING) as assetHealthScoreDescription,
    cast(t.`productionRate` as DOUBLE) as productionRate,
    cast(t.`productionRateUom` as STRING) as productionRateUom,
    cast(t.`name` as STRING) as name,
    cast(t.`description` as STRING) as description,
    case when t.`belongtoCity_externalId` is not null and trim(cast(t.`belongtoCity_externalId` as STRING)) != ''
         then node_reference('{{ isc_InstanceSpace }}', cast(t.`belongtoCity_externalId` as STRING))
         else null end as belongtoCity,
    case when t.`belongtoCostCenter_externalId` is not null and trim(cast(t.`belongtoCostCenter_externalId` as STRING)) != ''
         then node_reference('{{ isc_InstanceSpace }}', cast(t.`belongtoCostCenter_externalId` as STRING))
         else null end as belongtoCostCenter,
    node_reference('{{ isc_InstanceSpace }}', cast(t.`parent_externalId` as STRING)) as parent
FROM (
    SELECT *
    FROM `{{ btpSeedDbName }}`.`functional_asset`
    WHERE `parent_externalId` is not null
      AND trim(cast(`parent_externalId` as STRING)) != ''
) t
INNER JOIN cdf_data_models("{{ isc_AssetMaintenanceSchemaSpace }}", "AssetMaintenance", "{{dmVersion}}", "FunctionalAsset") p
    ON cast(t.`parent_externalId` as STRING) = p.`externalId`
    AND p.`space` = '{{ isc_InstanceSpace }}'
