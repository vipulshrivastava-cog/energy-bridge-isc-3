"""path_sync_with_file_cache — bootstrap backfill via sync file cache."""

from __future__ import annotations

import asyncio
from datetime import timedelta
from typing import Any

from cognite.client import CogniteClient
from cognite.client.data_classes.data_modeling.query import (
    NodeResultSetExpressionSync,
    QuerySync,
    SelectSync,
    SourceSelector,
)
from cognite.client.data_classes.filters import HasData

from common.client import resolve_async_client
from common.path_materializer import recompute_paths
from models import FileCacheSyncResult, HierarchyTaskInput


def _build_query_sync(task: HierarchyTaskInput) -> QuerySync:
    return QuerySync(
        with_={
            "nodes": NodeResultSetExpressionSync(
                filter=HasData(views=[task.view_id]),
                limit=task.chunk_size,
            )
        },
        select={
            "nodes": SelectSync(
                sources=[SourceSelector(source=task.view_id, properties=["parent"])]
            )
        },
    )


async def _run_path_sync_with_file_cache(
    client,
    task: HierarchyTaskInput,
) -> dict[str, object]:
    if not task.sync_file_external_id or task.security_category is None:
        raise ValueError(
            "SYNC_FILE_EXTERNAL_ID and SECURITY_CATEGORY_ID required for backfill mode"
        )

    session = client.data_modeling.instances.sync_with_file_cache(
        _build_query_sync(task),
        file_external_id=task.sync_file_external_id,
        security_category=task.security_category,
        backup_every=timedelta(minutes=15),
        backup_on_exit=True,
    )

    async with session:
        await session.sync_until_live()
        nodes = session.get_nodes("nodes")
        target_ids = {n.external_id for n in nodes}

    updated = await recompute_paths(client, task, target_ids)
    return FileCacheSyncResult(
        synced_nodes=len(target_ids),
        upserted_nodes=updated,
        view=task.view_label(),
    ).to_response()


def handle_path_sync_with_file_cache(
    task: HierarchyTaskInput, client: CogniteClient | None
) -> dict[str, Any]:
    async_client = resolve_async_client(client)
    return asyncio.run(_run_path_sync_with_file_cache(async_client, task))
