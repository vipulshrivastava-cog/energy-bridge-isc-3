"""Pydantic contracts for fn_btp_hierarchy (see pydantic-first-coding skill)."""

from __future__ import annotations

import json
import os
import uuid
from datetime import datetime
from typing import Any, Literal, Self

from cognite.client.data_classes.data_modeling.ids import ViewId
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

HierarchyType = Literal[
    "raw_ingest_incremental",
    "path_sync_cursor",
    "path_sync_with_file_cache",
    "initialize_sync_lock",
]

VALID_HIERARCHY_TYPES: tuple[HierarchyType, ...] = (
    "raw_ingest_incremental",
    "path_sync_cursor",
    "path_sync_with_file_cache",
    "initialize_sync_lock",
)

HandlerStatus = Literal["completed", "partial", "skipped"]

DEFAULT_MAX_RUNTIME_SECONDS = 480
DEFAULT_SCALAR_COLUMNS: dict[str, str] = {
    "name": "name",
    "description": "description",
    "hierarchyCode": "hierarchyCode",
    "hierarchyLevel": "hierarchyLevel",
    "hierarchyType": "hierarchyType",
    "locationCode": "locationCode",
    "locationType": "locationType",
    "isoCode": "isoCode",
    "latitude": "latitude",
    "longitude": "longitude",
    "physicalAddress": "physicalAddress",
    "companyCode": "companyCode",
    "controllingArea": "controllingArea",
    "costCenter": "costCenter",
    "profitCenter": "profitCenter",
    "purchasingOrg": "purchasingOrg",
    "currency": "currency",
    "hierarchyDepth": "hierarchyDepth",
    "productHierarchyCode": "productHierarchyCode",
    "productFamilyCode": "productFamilyCode",
    "productGroupCode": "productGroupCode",
    "isActive": "isActive",
    "declaredType": "declaredType",
    "sourceId": "sourceId",
    "sourceContext": "sourceContext",
    "sourceCreatedTime": "sourceCreatedTime",
    "sourceUpdatedTime": "sourceUpdatedTime",
}


class SyncLockConfig(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    enabled: bool = True
    ttl_seconds: int = 600
    heartbeat_seconds: int = 60

    @property
    def ttl_ms(self) -> int:
        return self.ttl_seconds * 1000


class NodeReference(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    space: str
    external_id: str = Field(alias="externalId")

    def to_wire(self) -> dict[str, str]:
        return self.model_dump(by_alias=True)


class SyncCursorState(BaseModel):
    cursor: str | None = None
    processed_count: int = 0
    job_run_id: str | None = None
    version: int | None = None


class SyncLockNodeState(BaseModel):
    orchestration_id: str = ""
    partition_id: str = Field(default="lock", alias="partitionId")
    last_updated: int = Field(default=0, alias="lastUpdated")

    @classmethod
    def from_node_properties(cls, props: dict[str, object]) -> Self:
        return cls.model_validate(
            {
                "orchestration_id": props.get("orchestration_id") or "",
                "partitionId": props.get("partitionId") or "lock",
                "lastUpdated": props.get("lastUpdated") or 0,
            }
        )


class DeferredIngestRow(BaseModel):
    external_id: str
    properties: dict[str, object] = Field(default_factory=dict)
    parent_external_id: str | None = None


class PathChain(BaseModel):
    root_id: str
    path_ids: list[str]


class HierarchyTaskInput(BaseModel):
    """Workflow / function task payload."""

    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    hierarchy_type: HierarchyType = "path_sync_cursor"
    sync_kind: Literal["node"] = "node"
    view_space: str
    view_external_id: str
    view_version: str
    instance_spaces: list[str]
    platform_space: str = "sp_isc_platform"
    platform_view_version: str | None = None
    chunk_size: int = 200
    max_runtime_seconds: int = DEFAULT_MAX_RUNTIME_SECONDS
    raw_db: str | None = None
    raw_table: str | None = None
    parent_column: str = "parent_externalId"
    batch_size: int = 10000
    scalar_columns: dict[str, str] = Field(default_factory=dict)
    sync_lock: SyncLockConfig = Field(default_factory=SyncLockConfig)
    function_call_id: str | None = None

    @field_validator("instance_spaces", mode="before")
    @classmethod
    def _parse_instance_spaces(cls, value: object) -> list[str]:
        if isinstance(value, list):
            return [str(item) for item in value if item]
        if isinstance(value, str):
            try:
                parsed = json.loads(value)
                if isinstance(parsed, list):
                    return [str(item) for item in parsed if item]
            except json.JSONDecodeError:
                return [value]
        return []

    @field_validator("scalar_columns", mode="before")
    @classmethod
    def _parse_scalar_columns(cls, value: object) -> dict[str, str]:
        if value is None:
            return {}
        if isinstance(value, str):
            parsed = json.loads(value)
            return {str(k): str(v) for k, v in dict(parsed).items()}
        if isinstance(value, dict):
            return {str(k): str(v) for k, v in value.items()}
        return {}

    @field_validator("chunk_size", "batch_size", "max_runtime_seconds", mode="before")
    @classmethod
    def _coerce_int(cls, value: object) -> object:
        if value is None or value == "":
            return value
        return int(value)

    @field_validator("sync_lock", mode="before")
    @classmethod
    def _parse_sync_lock(cls, value: object) -> object:
        if value is None:
            return SyncLockConfig()
        if isinstance(value, str):
            return SyncLockConfig.model_validate(json.loads(value))
        return value

    @model_validator(mode="after")
    def _defaults(self) -> Self:
        if not self.platform_view_version:
            object.__setattr__(self, "platform_view_version", self.view_version)
        return self

    @classmethod
    def from_workflow_data(cls, data: dict[str, object] | None) -> Self:
        payload = dict(data or {})
        env_defaults = {
            "view_space": os.environ.get("HIERARCHY_VIEW_SPACE"),
            "view_external_id": os.environ.get("HIERARCHY_VIEW_EXTERNAL_ID"),
            "view_version": os.environ.get("HIERARCHY_VIEW_VERSION"),
            "platform_space": os.getenv("PLATFORM_SPACE", "sp_isc_platform"),
            "hierarchy_type": os.getenv("HIERARCHY_TYPE", "path_sync_cursor"),
        }
        for key, value in env_defaults.items():
            if value and key not in payload:
                payload[key] = value

        if not payload.get("instance_spaces"):
            payload["instance_spaces"] = [
                os.environ.get("INSTANCE_SPACE", "sp_isc_supply_chain_instances")
            ]

        if "chunk_size" not in payload and os.getenv("SYNC_CHUNK_LIMIT"):
            payload["chunk_size"] = os.getenv("SYNC_CHUNK_LIMIT")

        return cls.model_validate(payload)

    @classmethod
    def from_function_payload(
        cls,
        data: dict[str, object] | None,
        *,
        function_call_info: dict[str, object] | None = None,
    ) -> Self:
        """Validate CDF `data` + optional call metadata (Pydantic-first contract)."""
        payload = dict(data or {})
        if function_call_info:
            call_id = function_call_info.get("call_id")
            if call_id is not None:
                payload["function_call_id"] = str(call_id)
        return cls.from_workflow_data(payload)

    @property
    def view_id(self) -> ViewId:
        return ViewId(
            space=self.view_space,
            external_id=self.view_external_id,
            version=self.view_version,
        )

    @property
    def primary_instance_space(self) -> str:
        return self.instance_spaces[0]

    @property
    def instance_space_key(self) -> str:
        return "+".join(sorted(self.instance_spaces))

    @property
    def lock_holder_id(self) -> str:
        return self.function_call_id or str(uuid.uuid4())

    @property
    def sync_file_external_id(self) -> str | None:
        return os.getenv("SYNC_FILE_EXTERNAL_ID")

    @property
    def security_category(self) -> int | None:
        raw = os.getenv("SECURITY_CATEGORY_ID")
        return int(raw) if raw else None

    def merged_scalar_columns(self) -> dict[str, str]:
        merged = dict(DEFAULT_SCALAR_COLUMNS)
        merged.update(self.scalar_columns)
        return merged

    def view_label(self) -> str:
        return f"{self.view_space}:{self.view_external_id}/{self.view_version}"


class HandlerResult(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    status: HandlerStatus
    mode: str
    reason: str | None = None

    def to_response(self) -> dict[str, object]:
        return self.model_dump(mode="json", by_alias=True, exclude_none=True)


class FunctionErrorResponse(BaseModel):
    """Dispatch / validation errors (DQV handler error shape)."""

    status: Literal["error"] = "error"
    error: str
    valid_types: list[str]

    def to_response(self) -> dict[str, object]:
        return self.model_dump(mode="json")


class SkippedResult(HandlerResult):
    status: Literal["skipped"] = "skipped"
    reason: str = "concurrent_execution"


class RawIngestResult(HandlerResult):
    status: Literal["completed", "partial"] = "completed"
    mode: Literal["raw_ingest_incremental"] = "raw_ingest_incremental"
    raw_db: str
    raw_table: str
    rows_scanned: int = 0
    upserted_nodes: int = 0
    deferred_nodes: int = 0
    cycles_rejected: int = 0
    cursor_advanced_to: int = 0
    view: str


class PathSyncResult(HandlerResult):
    status: Literal["completed", "partial"] = "completed"
    mode: Literal["path_sync_cursor"] = "path_sync_cursor"
    platform_space: str | None = None
    instance_spaces: list[str] | None = None
    chunks_processed: int = 0
    upserted_nodes: int = 0
    echo_chunks_skipped: int = 0
    processed_count: int = 0
    cursor_saved: bool | None = None
    elapsed_seconds: float | None = None
    view: str | None = None


class FileCacheSyncResult(HandlerResult):
    status: Literal["completed"] = "completed"
    mode: Literal["path_sync_with_file_cache"] = "path_sync_with_file_cache"
    synced_nodes: int
    upserted_nodes: int
    view: str


class InitializeLockResult(HandlerResult):
    status: Literal["completed"] = "completed"
    mode: Literal["initialize_sync_lock"] = "initialize_sync_lock"
    lock_node: str


ScalarValue = str | int | float | bool | datetime | None

_LOCATION_TYPE_TO_DECLARED: dict[str, str] = {
    "GeoRegion": "GeoRegion",
    "Country": "Country",
    "County": "County",
    "City": "City",
}

_HIERARCHY_TYPE_TO_DECLARED: dict[str, str] = {
    "Company": "Company",
    "ControllingArea": "ControllingArea",
    "BusinessUnit": "BusinessUnit",
    "CostCenter": "CostCenter",
    "ProfitCenter": "ProfitCenter",
    "PurchasingOrg": "PurchasingOrg",
    "Warehouse": "Warehouse",
    "Zone": "Zone",
    "StorageBin": "StorageBin",
}

_HIERARCHY_LEVEL_TO_DECLARED: dict[str, str] = {
    "ProductFamily": "ProductFamily",
    "ProductGroup": "ProductGroup",
}


def derive_declared_type(properties: dict[str, object]) -> str | None:
    """Map legacy discriminator columns to concrete view external ids (ADR 0009)."""
    existing = properties.get("declaredType")
    if existing is not None:
        if isinstance(existing, str) and existing.strip():
            return existing.strip()
        ext = getattr(existing, "external_id", None) or getattr(existing, "externalId", None)
        if isinstance(ext, str) and ext.strip():
            return ext.strip()
        if isinstance(existing, dict):
            ext_dict = existing.get("externalId") or existing.get("external_id")
            if isinstance(ext_dict, str) and ext_dict.strip():
                return ext_dict.strip()
    location_type = properties.get("locationType")
    if isinstance(location_type, str) and location_type in _LOCATION_TYPE_TO_DECLARED:
        return _LOCATION_TYPE_TO_DECLARED[location_type]
    hierarchy_type = properties.get("hierarchyType")
    if isinstance(hierarchy_type, str) and hierarchy_type in _HIERARCHY_TYPE_TO_DECLARED:
        return _HIERARCHY_TYPE_TO_DECLARED[hierarchy_type]
    hierarchy_level = properties.get("hierarchyLevel")
    if isinstance(hierarchy_level, str) and hierarchy_level in _HIERARCHY_LEVEL_TO_DECLARED:
        return _HIERARCHY_LEVEL_TO_DECLARED[hierarchy_level]
    return None


def coerce_scalar(value: object, view_property: str) -> ScalarValue:
    if value is None:
        return None
    if view_property in {"latitude", "longitude"}:
        try:
            return float(value)  # type: ignore[arg-type]
        except (TypeError, ValueError):
            return None
    if view_property == "hierarchyDepth":
        try:
            return int(value)  # type: ignore[arg-type]
        except (TypeError, ValueError):
            return None
    if view_property == "isActive":
        if isinstance(value, bool):
            return value
        return str(value).lower() in {"true", "1", "yes"}
    if view_property in {"sourceCreatedTime", "sourceUpdatedTime"}:
        return str(value) if value is not None else None
    text = str(value).strip()
    return text if text else None
