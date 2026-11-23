"""Per-view execution lease (ADR-0007) — async port of DQV cursor_state lock helpers."""

from __future__ import annotations

import time

from cognite.client import AsyncCogniteClient

from common.cursor_state import refresh_sync_lock, release_sync_lock, try_acquire_sync_lock
from models import HierarchyTaskInput, SyncLockConfig


class SyncLockSession:
    def __init__(
        self,
        client: AsyncCogniteClient,
        task: HierarchyTaskInput,
        lock_cfg: SyncLockConfig,
    ) -> None:
        self.client = client
        self.task = task
        self.lock_cfg = lock_cfg
        self.holder_id = task.lock_holder_id
        self.lock_version: int | None = None
        self.last_heartbeat = time.time()
        self.acquired = False

    async def acquire(self) -> bool:
        if not self.lock_cfg.enabled:
            self.acquired = True
            return True
        acquired, self.lock_version = await try_acquire_sync_lock(
            self.client,
            self.task.view_space,
            self.task.view_external_id,
            self.task.instance_space_key,
            self.holder_id,
            self.lock_cfg.ttl_ms,
            self.task.platform_space,
            self.task.platform_view_version,
        )
        self.acquired = acquired
        if acquired:
            self.last_heartbeat = time.time()
        return acquired

    async def heartbeat(self) -> bool:
        if not self.lock_cfg.enabled or not self.acquired:
            return True
        now = time.time()
        if now - self.last_heartbeat < self.lock_cfg.heartbeat_seconds:
            return True
        ok, self.lock_version = await refresh_sync_lock(
            self.client,
            self.task.view_space,
            self.task.view_external_id,
            self.task.instance_space_key,
            self.holder_id,
            self.lock_cfg.ttl_ms,
            self.task.platform_space,
            self.task.platform_view_version,
            known_version=self.lock_version,
        )
        if ok:
            self.last_heartbeat = now
        return ok

    async def release(self) -> None:
        if not self.lock_cfg.enabled or not self.acquired:
            return
        await release_sync_lock(
            self.client,
            self.task.view_space,
            self.task.view_external_id,
            self.task.instance_space_key,
            self.holder_id,
            self.task.platform_space,
            self.task.platform_view_version,
            known_version=self.lock_version,
        )
