from __future__ import annotations

from typing import Any, TYPE_CHECKING

from django.db import transaction

from django_spire.contrib.sync.database.conflict import FieldTimestampWins
from django_spire.contrib.sync.database.engine import (
    BATCH_BYTES_DEFAULT,
    DatabaseEngine,
)
from django_spire.contrib.sync.database.reconciler import PayloadReconciler
from django_spire.contrib.sync.django.graph import build_graph
from django_spire.contrib.sync.django.lock import DjangoSyncLock
from django_spire.contrib.sync.django.mixin import SyncableMixin
from django_spire.contrib.sync.django.storage import DjangoSyncStorage
from django_spire.contrib.sync.django.views import process_sync_request

if TYPE_CHECKING:
    from collections.abc import Callable
    from contextlib import AbstractContextManager

    from django.http import HttpRequest, JsonResponse

    from django_spire.contrib.sync.core.clock import HybridLogicalClock
    from django_spire.contrib.sync.core.enums import SyncPhase, SyncStage
    from django_spire.contrib.sync.database.conflict import ConflictResolver
    from django_spire.contrib.sync.database.graph import DependencyGraph
    from django_spire.contrib.sync.database.lock import SyncLock
    from django_spire.contrib.sync.database.manifest import (
        DatabaseResult,
        SyncManifest,
    )
    from django_spire.contrib.sync.database.storage import DatabaseSyncStorage


class SyncServer:
    def __init__(
        self,
        models: list[type[SyncableMixin]],
        node_id: str,
        *,
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
        self._engine = DatabaseEngine(
            batch_bytes=batch_bytes,
            batch_size=batch_size,
            clock=clock or SyncableMixin.get_clock(),
            clock_drift_max=clock_drift_max,
            graph=graph or build_graph(models),
            lock=lock or DjangoSyncLock(),
            node_id=node_id,
            on_complete=on_complete,
            on_phase=on_phase,
            payload_bytes_max=payload_bytes_max,
            payload_records_max=payload_records_max,
            progress=progress,
            reconciler=PayloadReconciler(
                resolver=resolver or FieldTimestampWins(),
            ),
            storage=storage or DjangoSyncStorage(models=models),
            transaction=transaction_fn,
        )

    def handle(
        self, incoming: SyncManifest,
    ) -> tuple[SyncManifest, DatabaseResult]:
        return self._engine.process(incoming)

    def serve(
        self,
        request: HttpRequest,
        validate_node_id: Callable[[HttpRequest, str], bool] | None = None,
    ) -> JsonResponse:
        return process_sync_request(
            request,
            self._engine,
            validate_node_id=validate_node_id,
        )
