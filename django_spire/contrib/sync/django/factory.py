from __future__ import annotations

from typing import Any, TYPE_CHECKING

from django.db import transaction

from django_spire.contrib.sync.database.conflict import FieldTimestampWins
from django_spire.contrib.sync.database.engine import DatabaseEngine
from django_spire.contrib.sync.database.reconciler import PayloadReconciler
from django_spire.contrib.sync.database.transport.http import HttpTransport
from django_spire.contrib.sync.django.graph import build_graph
from django_spire.contrib.sync.django.lock import DjangoSyncLock
from django_spire.contrib.sync.django.mixin import SyncableMixin
from django_spire.contrib.sync.django.storage import DjangoSyncStorage

if TYPE_CHECKING:
    from collections.abc import Callable
    from contextlib import AbstractContextManager

    from django_spire.contrib.sync.core.clock import HybridLogicalClock
    from django_spire.contrib.sync.core.enums import SyncPhase, SyncStage
    from django_spire.contrib.sync.database.conflict import ConflictResolver
    from django_spire.contrib.sync.database.graph import DependencyGraph
    from django_spire.contrib.sync.database.lock import SyncLock
    from django_spire.contrib.sync.database.manifest import DatabaseResult
    from django_spire.contrib.sync.database.storage import DatabaseSyncStorage


def _resolve_common(
    models: list[type[SyncableMixin]],
    clock: HybridLogicalClock | None,
    graph: DependencyGraph | None,
    resolver: ConflictResolver | None,
    storage: DatabaseSyncStorage | None,
) -> tuple[
    HybridLogicalClock,
    DependencyGraph,
    PayloadReconciler,
    DatabaseSyncStorage,
]:
    resolved_clock = clock or SyncableMixin.get_clock()
    resolved_graph = graph or build_graph(models)
    resolved_reconciler = PayloadReconciler(
        resolver=resolver or FieldTimestampWins(),
    )
    resolved_storage = storage or DjangoSyncStorage(
        models=models,
    )

    return resolved_clock, resolved_graph, resolved_reconciler, resolved_storage


def build_client_engine(
    models: list[type[SyncableMixin]],
    node_id: str,
    url: str,
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
    transaction_fn: Callable[[], AbstractContextManager[Any]] = transaction.atomic,
) -> DatabaseEngine:
    resolved_clock, resolved_graph, reconciler, resolved_storage = _resolve_common(
        models, clock, graph, resolver, storage,
    )

    return DatabaseEngine(
        clock=resolved_clock,
        clock_drift_max=clock_drift_max,
        graph=resolved_graph,
        node_id=node_id,
        on_complete=on_complete,
        on_phase=on_phase,
        progress=progress,
        reconciler=reconciler,
        storage=resolved_storage,
        transaction=transaction_fn,
        transport=HttpTransport(url=url, headers=headers or {}),
    )


def build_server_engine(
    models: list[type[SyncableMixin]],
    node_id: str,
    *,
    clock: HybridLogicalClock | None = None,
    clock_drift_max: int | None = 300,
    graph: DependencyGraph | None = None,
    lock: SyncLock | None = None,
    on_complete: Callable[[DatabaseResult], None] | None = None,
    on_phase: Callable[[SyncPhase], None] | None = None,
    progress: Callable[[SyncStage, int, int], None] | None = None,
    resolver: ConflictResolver | None = None,
    storage: DatabaseSyncStorage | None = None,
    transaction_fn: Callable[[], AbstractContextManager[Any]] = transaction.atomic,
) -> DatabaseEngine:
    resolved_clock, resolved_graph, reconciler, resolved_storage = _resolve_common(
        models, clock, graph, resolver, storage,
    )

    return DatabaseEngine(
        clock=resolved_clock,
        clock_drift_max=clock_drift_max,
        graph=resolved_graph,
        lock=lock or DjangoSyncLock(),
        node_id=node_id,
        on_complete=on_complete,
        on_phase=on_phase,
        progress=progress,
        reconciler=reconciler,
        storage=resolved_storage,
        transaction=transaction_fn,
    )
