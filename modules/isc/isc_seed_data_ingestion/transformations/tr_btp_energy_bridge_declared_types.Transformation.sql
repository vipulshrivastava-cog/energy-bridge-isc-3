-- Transformation: tr_btp_energy_bridge_declared_types
-- Source: inline values (no RAW table needed)
-- Target: DeclaredTypes ({{ isc_OrganizationalFoundationSchemaSpace }}:OrganizationalFoundation/{{dmVersion}})
-- Instance space: {{ isc_OrganizationalFoundationSchemaSpace }} (DeclaredTypes catalog must live in this schema space to match the `declaredType` equals filters hardcoded in GeoRegion/Country/City/Company/BusinessUnit/CostCenter/Warehouse/Zone/StorageBin/ProductSector/ProductFamily/ProductGroup/ProductSubgroup views)
--
-- Seeds the DeclaredTypes catalog. Node externalIds equal the concrete view
-- externalIds (City, Warehouse, ...) so that `declaredType` on the shared
-- GeoLocations / BusinessUnits / StorageLocations nodes points at an existing node.

SELECT
    cast(externalId as STRING) as externalId,
    '{{ isc_OrganizationalFoundationSchemaSpace }}' as space,
    cast(name as STRING) as name,
    cast(description as STRING) as description,
    cast(used_by_container as STRING) as used_by_container
FROM VALUES
    ('GeoRegion', 'GeoRegion', 'Top-level geographic region grouping countries.', 'GeoLocations'),
    ('Country', 'Country', 'Country-level geographic node.', 'GeoLocations'),
    ('City', 'City', 'City or locality; anchor for functional assets and warehouses.', 'GeoLocations'),
    ('Company', 'Company', 'Legal entity at the top of the organisational hierarchy.', 'BusinessUnits'),
    ('BusinessUnit', 'BusinessUnit', 'Business unit within a company.', 'BusinessUnits'),
    ('CostCenter', 'CostCenter', 'Cost center accountable for assets and spend.', 'BusinessUnits'),
    ('Warehouse', 'Warehouse', 'Warehouse or storage site.', 'StorageLocations'),
    ('Zone', 'Zone', 'Zone within a warehouse.', 'StorageLocations'),
    ('StorageBin', 'StorageBin', 'Storage bin within a zone.', 'StorageLocations')
    ('ProductFamily', 'ProductFamily', 'Product family in the product classification hierarchy.', 'Products'),
    ('ProductGroup', 'ProductGroup', 'Product group in the product classification hierarchy.', 'Products')
    AS t(externalId, name, description, used_by_container)
