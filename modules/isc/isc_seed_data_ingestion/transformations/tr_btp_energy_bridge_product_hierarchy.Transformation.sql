SELECT
cast(`key` AS STRING) AS externalId,
'{{ isc_InstanceSpace }}' AS space,
cast(`name` AS STRING) AS name,
cast(`description` AS STRING) AS description,
cast(`hierarchyCode` AS STRING) AS hierarchyCode,
CASE
WHEN `hierarchyDepth` IS NOT NULL AND trim(cast(`hierarchyDepth` AS STRING)) != ''
THEN cast(`hierarchyDepth` AS INT) ELSE NULL
END AS hierarchyDepth,
cast(`productHierarchyCode` AS STRING) AS productHierarchyCode,
cast(`productFamilyCode` AS STRING) AS productFamilyCode,
cast(`productGroupCode` AS STRING) AS productGroupCode,
CASE
WHEN `isActive` IS NOT NULL AND trim(cast(`isActive` AS STRING)) != ''
THEN cast(`isActive` AS BOOLEAN) ELSE NULL
END AS isActive,
cast(`sourceId` AS STRING) AS sourceId,
cast(`sourceContext` AS STRING) AS sourceContext,
cast(`sourceCreatedTime` AS TIMESTAMP) AS sourceCreatedTime,
cast(`sourceUpdatedTime` AS TIMESTAMP) AS sourceUpdatedTime,
CASE cast(`hierarchyLevel` AS STRING)
WHEN 'ProductFamily' THEN node_reference('{{ isc_OrganizationalFoundationSchemaSpace }}', 'ProductFamily')
WHEN 'ProductGroup' THEN node_reference('{{ isc_OrganizationalFoundationSchemaSpace }}', 'ProductGroup')
ELSE NULL
END AS declaredType,
CASE
WHEN `parent_externalId` IS NULL OR trim(cast(`parent_externalId` AS STRING)) = '' THEN NULL
ELSE node_reference('{{ isc_InstanceSpace }}', cast(`parent_externalId` AS STRING))
END AS parent
FROM
`{{ btpSeedDbName }}`.`product_hierarchy`
