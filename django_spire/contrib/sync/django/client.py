from __future__ import annotations

from typing import Any, TYPE_CHECKING

from django.db import transaction

from django_spire.contrib.sync.database.conflict import FieldTimestampWins
from django_spire.contrib.sync.database.engine import DatabaseEngine
from django_spire.contrib.sync.database.reconciler import PayloadReconciler
from django_spire.contrib.sync.django.graph import build_graph
from django_spire.contrib.sync.django.mixin import SyncableMixin
from django_spire.contrib.sync.django.storage import DjangoSyncStorage

if TYPE_CHECKING:
    from collections.abc import Callable
    from contextlib import AbstractContextManager

    from django_spire.contrib.sync.core.clock import HybridLogicalClock
    from django_spire.contrib.sync.core.enums import SyncPhase, SyncStage
    from django_spire.contrib.sync.database.conflict import ConflictResolver
    from django_spire.contrib.sync.database.graph import DependencyGraph
    from django_spire.contrib.sync.database.manifest import DatabaseResult
    from django_spire.contrib.sync.database.storage import DatabaseSyncStorage
    from django_spire.contrib.sync.database.transport.base import Transport


class SyncClient:
    def __init__(
        self,
        models: list[type[SyncableMixin]],
        node_id: str,
        transport: Transport,
        *,
        clock: HybridLogicalClock | None = None,
        clock_drift_max: int | None = 300,
        graph: DependencyGraph | None = None,
        on_complete: Callable[[DatabaseResult], None] | None = None,
        on_phase: Callable[[SyncPhase], None] | None = None,
        progress: Callable[[SyncStage, int, int], None] | None = None,
        resolver: ConflictResolver | None = None,
        storage: DatabaseSyncStorage | None = None,
        transaction_fn: Callable[[], AbstractContextManager[Any]] = transaction.atomic,
    ) -> None:
        self._engine = DatabaseEngine(
            clock=clock or SyncableMixin.get_clock(),
            clock_drift_max=clock_drift_max,
            graph=graph or build_graph(models),
            node_id=node_id,
            on_complete=on_complete,
            on_phase=on_phase,
            progress=progress,
            reconciler=PayloadReconciler(resolver=resolver or FieldTimestampWins()),
            storage=storage or DjangoSyncStorage(models=models),
            transaction=transaction_fn,
            transport=transport,
        )

    def sync(self, dry_run: bool = False) -> DatabaseResult:
        return self._engine.sync(dry_run=dry_run)
