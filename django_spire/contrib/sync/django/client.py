from __future__ import annotations

from typing import Any, TYPE_CHECKING

from django_spire.contrib.sync.django.factory import build_client_engine

if TYPE_CHECKING:
    from collections.abc import Callable
    from contextlib import AbstractContextManager

    from django_spire.contrib.sync.core.clock import HybridLogicalClock
    from django_spire.contrib.sync.core.enums import SyncPhase, SyncStage
    from django_spire.contrib.sync.database.conflict import ConflictResolver
    from django_spire.contrib.sync.database.graph import DependencyGraph
    from django_spire.contrib.sync.database.manifest import DatabaseResult
    from django_spire.contrib.sync.database.storage import DatabaseSyncStorage
    from django_spire.contrib.sync.django.mixin import SyncableMixin


class SyncClient:
    def __init__(
        self,
        models: list[type[SyncableMixin]],
        node_id: str,
        server_url: str,
        *,
        clock: HybridLogicalClock | None = None,
        clock_drift_max: int | None = 300,
        graph: DependencyGraph | None = None,
        headers: dict[str, str] | None = None,
        on_complete: Callable[[DatabaseResult], None] | None = None,
        on_phase: Callable[[SyncPhase], None] | None = None,
        progress: Callable[[SyncStage, int, int], None] | None = None,
        resolver: ConflictResolver | None = None,
        storage: DatabaseSyncStorage | None = None,
        transaction_fn: Callable[[], AbstractContextManager[Any]] | None = None,
    ) -> None:
        kwargs: dict[str, Any] = {
            'clock': clock,
            'clock_drift_max': clock_drift_max,
            'graph': graph,
            'headers': headers,
            'on_complete': on_complete,
            'on_phase': on_phase,
            'progress': progress,
            'resolver': resolver,
            'storage': storage,
        }

        if transaction_fn is not None:
            kwargs['transaction_fn'] = transaction_fn

        self._engine = build_client_engine(
            models=models,
            node_id=node_id,
            url=server_url,
            **kwargs,
        )

    def sync(self, dry_run: bool = False) -> DatabaseResult:
        return self._engine.sync(dry_run=dry_run)
