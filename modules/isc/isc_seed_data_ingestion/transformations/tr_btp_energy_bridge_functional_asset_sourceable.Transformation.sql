-- Transformation: tr_btp_energy_bridge_functional_asset_sourceable
-- Source: {{ btpSeedDbName }}.functional_asset (RAW)
-- Target: CogniteSourceable (cdf_cdm:CogniteCore/v1)
-- Instance space: {{ isc_InstanceSpace }}

-- Purpose: presence rows so cdf_cdm.CogniteAsset's requires(CogniteSourceable) constraint is met.
-- The `source` relation is not written (CogniteSourceSystem cannot be auto-created).

SELECT
    cast(`key` as STRING) as externalId,
    '{{ isc_InstanceSpace }}' as space,
    cast(`sourceId` as STRING) as sourceId,
    cast(`sourceContext` as STRING) as sourceContext,
    cast(`sourceCreatedTime` as STRING) as sourceCreatedTime,
    cast(`sourceUpdatedTime` as STRING) as sourceUpdatedTime,
    cast(`sourceCreatedUser` as STRING) as sourceCreatedUser,
    cast(`sourceUpdatedUser` as STRING) as sourceUpdatedUser
FROM
    `{{ btpSeedDbName }}`.`functional_asset`
