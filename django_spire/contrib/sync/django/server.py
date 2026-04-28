from __future__ import annotations

from typing import Any, TYPE_CHECKING

from django_spire.contrib.sync.django.factory import build_server_engine
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
    from django_spire.contrib.sync.database.manifest import DatabaseResult, SyncManifest
    from django_spire.contrib.sync.database.storage import DatabaseSyncStorage
    from django_spire.contrib.sync.django.mixin import SyncableMixin


class SyncServer:
    def __init__(
        self,
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
        transaction_fn: Callable[[], AbstractContextManager[Any]] | None = None,
    ) -> None:
        kwargs: dict[str, Any] = {
            'clock': clock,
            'clock_drift_max': clock_drift_max,
            'graph': graph,
            'lock': lock,
            'on_complete': on_complete,
            'on_phase': on_phase,
            'progress': progress,
            'resolver': resolver,
            'storage': storage,
        }

        if transaction_fn is not None:
            kwargs['transaction_fn'] = transaction_fn

        self._engine = build_server_engine(
            models=models,
            node_id=node_id,
            **kwargs,
        )

    def handle(
        self,
        incoming: SyncManifest,
    ) -> tuple[SyncManifest, DatabaseResult]:
        return self._engine.process(incoming)

    def serve(
        self,
        request: HttpRequest,
        validate_node_id: Callable[[HttpRequest, str], bool] | None = None,
    ) -> JsonResponse:
        return process_sync_request(
            request, self._engine,
            validate_node_id=validate_node_id,
        )
