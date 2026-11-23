"""initialize_sync_lock — deploy-time lock placeholder (DQV initialize_sync_lock_node)."""

from __future__ import annotations

import asyncio
from typing import Any

from cognite.client import CogniteClient

from common.client import resolve_async_client
from common.cursor_state import initialize_sync_lock_node, sync_lock_external_id
from models import HierarchyTaskInput, InitializeLockResult


async def _run_initialize_sync_lock(
    client,
    task: HierarchyTaskInput,
) -> dict[str, object]:
    await initialize_sync_lock_node(
        client,
        task.view_space,
        task.view_external_id,
        task.instance_space_key,
        task.platform_space,
        task.platform_view_version,
    )
    lock_node = sync_lock_external_id(
        task.view_space, task.view_external_id, task.instance_space_key
    )
    return InitializeLockResult(lock_node=lock_node).to_response()


def handle_initialize_sync_lock(
    task: HierarchyTaskInput, client: CogniteClient | None
) -> dict[str, Any]:
    async_client = resolve_async_client(client)
    return asyncio.run(_run_initialize_sync_lock(async_client, task))
