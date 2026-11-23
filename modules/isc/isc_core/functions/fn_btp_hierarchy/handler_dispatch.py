"""Dispatch logic separated from CDF entrypoint (handler.py)."""

from __future__ import annotations

from typing import Any

from pydantic import ValidationError

from handlers.initialize_sync_lock import handle_initialize_sync_lock
from handlers.path_sync_cursor import handle_path_sync_cursor
from handlers.path_sync_with_file_cache import handle_path_sync_with_file_cache
from handlers.raw_ingest_incremental import handle_raw_ingest_incremental
from models import VALID_HIERARCHY_TYPES, FunctionErrorResponse, HierarchyTaskInput

_DISPATCH = {
    "raw_ingest_incremental": handle_raw_ingest_incremental,
    "path_sync_cursor": handle_path_sync_cursor,
    "path_sync_with_file_cache": handle_path_sync_with_file_cache,
    "initialize_sync_lock": handle_initialize_sync_lock,
}


def dispatch(
    data: dict | None,
    function_call_info: dict | None,
    client: Any,
) -> dict[str, object]:
    try:
        task = HierarchyTaskInput.from_function_payload(
            data, function_call_info=function_call_info
        )
    except ValidationError as exc:
        return FunctionErrorResponse(
            error=str(exc),
            valid_types=list(VALID_HIERARCHY_TYPES),
        ).to_response()

    handler_fn = _DISPATCH.get(task.hierarchy_type)
    if handler_fn is None:
        return FunctionErrorResponse(
            error=f"Unknown hierarchy_type: '{task.hierarchy_type}'",
            valid_types=list(VALID_HIERARCHY_TYPES),
        ).to_response()

    return handler_fn(task, client)
