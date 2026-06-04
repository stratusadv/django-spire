from __future__ import annotations

from typing import Any, TYPE_CHECKING

from django.db import transaction

from django_spire.sync.database.conflict import FieldTimestampWins
from django_spire.sync.database.engine import BATCH_BYTES_DEFAULT, DatabaseEngine
from django_spire.sync.database.reconciler import PayloadReconciler
from django_spire.sync.django.graph import (
    build_graph,
    get_deferred_foreign_key_columns,
    get_foreign_key_columns_for_cascade,
)
from django_spire.sync.django.mixin import SyncableMixin
from django_spire.sync.django.storage import DjangoSyncStorage

if TYPE_CHECKING:
    from collections.abc import Callable
    from contextlib import AbstractContextManager

    from django_spire.sync.core.clock import HybridLogicalClock
    from django_spire.sync.core.enums import SyncPhase, SyncStage
    from django_spire.sync.database.conflict import ConflictResolver
    from django_spire.sync.database.graph import DependencyGraph
    from django_spire.sync.database.lock import SyncLock
    from django_spire.sync.database.manifest import DatabaseResult
    from django_spire.sync.database.storage import DatabaseSyncStorage
    from django_spire.sync.database.transport.base import Transport


class SyncClient:
    def __init__(
        self,
        models: list[type[SyncableMixin]],
        node_id: str,
        transport: Transport,
        *,
        peer_node_id: str,
        batch_bytes: int | None = BATCH_BYTES_DEFAULT,
        batch_size: int | None = None,
        clock: HybridLogicalClock | None = None,
        clock_drift_max: int | None = 300,
        graph: DependencyGraph | None = None,
        lock: SyncLock | None = None,
        on_complete: Callable[[DatabaseResult], None] | None = None,
        on_phase: Callable[[SyncPhase], None] | None = None,
        payload_bytes_max: int | None = None,
        payload_records_max: int | None = None,
        progress: Callable[[SyncStage, int, int], None] | None = None,
        resolver: ConflictResolver | None = None,
        storage: DatabaseSyncStorage | None = None,
        transaction_fn: Callable[[], AbstractContextManager[Any]] = transaction.atomic,
    ) -> None:
        resolved_graph = graph or build_graph(models)

        deferred_foreign_keys = get_deferred_foreign_key_columns(models, resolved_graph)

        foreign_key_columns = get_foreign_key_columns_for_cascade(models)

        self._engine = DatabaseEngine(
            batch_bytes=batch_bytes,
            batch_size=batch_size,
            clock=clock or SyncableMixin.get_clock(),
            clock_drift_max=clock_drift_max,
            foreign_key_columns=foreign_key_columns,
            graph=resolved_graph,
            lock=lock,
            node_id=node_id,
            on_complete=on_complete,
            on_phase=on_phase,
            payload_bytes_max=payload_bytes_max,
            payload_records_max=payload_records_max,
            peer_node_id=peer_node_id,
            progress=progress,
            reconciler=PayloadReconciler(resolver=resolver or FieldTimestampWins()),
            storage=storage
            or DjangoSyncStorage(models=models, deferred_foreign_keys=deferred_foreign_keys),
            transaction=transaction_fn,
            transport=transport,
        )

    def sync(self, dry_run: bool = False) -> DatabaseResult:
        return self._engine.sync(dry_run=dry_run)
