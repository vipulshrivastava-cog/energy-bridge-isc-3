-- Transformation: tr_btp_energy_bridge_functional_asset_visualizable
-- Source: {{ btpSeedDbName }}.functional_asset (RAW)
-- Target: CogniteVisualizable (cdf_cdm:CogniteCore/v1)
-- Instance space: {{ isc_InstanceSpace }}

-- Purpose: presence rows so cdf_cdm.CogniteAsset's requires(CogniteVisualizable) constraint is met.

SELECT
    cast(`key` as STRING) as externalId,
    '{{ isc_InstanceSpace }}' as space,
    null as object3D
FROM
    `{{ btpSeedDbName }}`.`functional_asset`
