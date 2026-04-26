from __future__ import annotations

from decimal import Decimal

from typing_extensions import TYPE_CHECKING

from django_spire.contrib.service import BaseDjangoModelService
from django_spire.contrib.sync.core.clock import HybridLogicalClock
from django_spire.contrib.sync.database.conflict import (
    ConflictResolver,
    FieldOwnershipWins,
    FieldTimestampWins,
    LocalWins,
    RemoteWins,
)
from django_spire.contrib.sync.database.engine import DatabaseEngine
from django_spire.contrib.sync.database.graph import DependencyGraph
from django_spire.contrib.sync.database.reconciler import PayloadReconciler
from django_spire.contrib.sync.django.queryset import sync_bypass
from django_spire.contrib.sync.tests.database.helpers import InMemoryDatabaseStorage

from test_project.apps.sync.config import (
    TABLET_COUNT_DEFAULT,
    get_active_tablet_databases,
)
from test_project.apps.sync.constants import (
    DEFAULT_STRATEGY,
    RESULT_CATEGORIES,
    SyncModelLabel,
    SyncStrategy,
    WinnerSide,
)
from test_project.apps.sync.context import switch_database
from test_project.apps.sync.registry import (
    CREW_FIELDS,
    MODEL_CONFIG,
    MODEL_LABELS,
    OFFICE_FIELDS,
)
from test_project.apps.sync.types import (
    ConflictLogEntry,
    FieldConflictDetail,
    SerializedSyncResult,
    SyncPerformResult,
    TabletSyncData,
)

if TYPE_CHECKING:
    from typing_extensions import Any

    from django_spire.contrib.sync.database.manifest import SyncManifest

    from test_project.apps.sync.models import Client


DEPENDENCY_GRAPH = DependencyGraph({
    SyncModelLabel.CLIENT: set(),
    SyncModelLabel.SITE: {SyncModelLabel.CLIENT},
    SyncModelLabel.SURVEY_PLAN: {SyncModelLabel.SITE},
    SyncModelLabel.STAKE: {SyncModelLabel.SURVEY_PLAN},
})


def _coerce_value(value: Any) -> Any:
    if isinstance(value, Decimal):
        return float(value)
    return value


class SyncProcessorService(BaseDjangoModelService['Client']):
    obj: Client

    def perform_sync(
        self,
        strategy: str = DEFAULT_STRATEGY,
        tablet_count: int = TABLET_COUNT_DEFAULT,
        tablet_databases: list[str] | None = None,
    ) -> SyncPerformResult:
        clock = HybridLogicalClock()

        if tablet_databases is None:
            tablet_databases = get_active_tablet_databases(tablet_count)

        tablet_results: dict[str, TabletSyncData] = {}

        for tablet_database in tablet_databases:
            tablet_result = self._sync_tablet(clock, tablet_database, strategy)
            tablet_results[tablet_database] = tablet_result

        if len(tablet_databases) > 1:
            for tablet_database in tablet_databases:
                convergence_result = self._sync_tablet(clock, tablet_database, strategy)
                tablet_results[tablet_database] = self._merge_results(
                    tablet_results[tablet_database], convergence_result,
                )

        return SyncPerformResult(
            strategy=strategy,
            sync_order=DEPENDENCY_GRAPH.sync_order(),
            tablet_count=tablet_count,
            tablets=tablet_results,
        )

    def _apply_response(self, engine: DatabaseEngine, response: SyncManifest) -> None:
        payload_map = {payload.model_label: payload for payload in response.payloads}

        for label in DEPENDENCY_GRAPH.sync_order():
            payload = payload_map.get(label)

            if not payload:
                continue

            config = MODEL_CONFIG[label]

            for key, record in payload.records.items():
                data = {}

                for field_name in config.fields:
                    if field_name in record.data:
                        data[field_name] = _coerce_value(record.data[field_name])

                for foreign_key in config.foreign_key_fields:
                    if foreign_key in record.data:
                        data[foreign_key] = record.data[foreign_key]

                engine._storage.seed(label, key, data, record.timestamps)

    @staticmethod
    def _build_engine(clock: HybridLogicalClock, database_name: str, resolver: ConflictResolver) -> DatabaseEngine:
        return DatabaseEngine(
            clock=clock,
            graph=DEPENDENCY_GRAPH,
            reconciler=PayloadReconciler(resolver),
            storage=InMemoryDatabaseStorage(models=MODEL_LABELS),
        )

    @staticmethod
    def _build_resolvers(strategy: str) -> tuple[ConflictResolver, ConflictResolver]:
        resolver_map = {
            SyncStrategy.FIELD_OWNERSHIP: (
                FieldOwnershipWins(local_fields=CREW_FIELDS, remote_fields=OFFICE_FIELDS),
                FieldOwnershipWins(local_fields=OFFICE_FIELDS, remote_fields=CREW_FIELDS),
            ),
            SyncStrategy.FIELD_TIMESTAMP_WINS: (FieldTimestampWins(), FieldTimestampWins()),
            SyncStrategy.LOCAL_WINS: (LocalWins(), RemoteWins()),
            SyncStrategy.REMOTE_WINS: (RemoteWins(), LocalWins()),
        }
        return resolver_map.get(strategy, (FieldTimestampWins(), FieldTimestampWins()))

    @staticmethod
    def _determine_winner(resolution_source: str, timestamps: dict) -> str:
        if resolution_source == WinnerSide.LOCAL:
            return WinnerSide.LOCAL

        if resolution_source == WinnerSide.REMOTE:
            return WinnerSide.REMOTE

        if timestamps.get('remote_timestamp', 0) >= timestamps.get('local_timestamp', 0):
            return WinnerSide.REMOTE

        return WinnerSide.LOCAL

    @staticmethod
    def _load_from_orm(engine: DatabaseEngine, database_name: str) -> int:
        switch_database(database_name)
        record_count = 0

        with sync_bypass():
            for label in DEPENDENCY_GRAPH.sync_order():
                config = MODEL_CONFIG[label]

                for instance in config.model.objects.all():
                    key = str(instance.pk)
                    data = {}

                    for field_name in config.fields:
                        data[field_name] = _coerce_value(getattr(instance, field_name))

                    for foreign_key in config.foreign_key_fields:
                        data[foreign_key] = str(getattr(instance, foreign_key)) if getattr(instance, foreign_key) else None

                    timestamp_map = getattr(instance, 'sync_field_timestamps', {}) or {}
                    engine._storage.seed(label, key, data, timestamp_map)
                    record_count += 1

        return record_count

    @staticmethod
    def _merge_results(
        first: TabletSyncData,
        second: TabletSyncData,
    ) -> TabletSyncData:
        merged_result = SerializedSyncResult()

        for category in RESULT_CATEGORIES:
            first_data = getattr(first.tablet_result, category)
            second_data = getattr(second.tablet_result, category)
            combined: dict[str, list[str]] = {}

            for label in set(first_data) | set(second_data):
                keys = list(dict.fromkeys(
                    first_data.get(label, []) + second_data.get(label, [])
                ))
                combined[label] = keys

            setattr(merged_result, category, combined)

        merged_result.errors = first.tablet_result.errors + second.tablet_result.errors
        merged_result.conflict_log = first.tablet_result.conflict_log + second.tablet_result.conflict_log

        return TabletSyncData(
            cloud_record_count=second.cloud_record_count,
            cloud_result=first.cloud_result,
            tablet_record_count=first.tablet_record_count,
            tablet_result=merged_result,
        )

    @staticmethod
    def _persist_to_orm(engine: DatabaseEngine, database_name: str) -> None:
        switch_database(database_name)

        for label in DEPENDENCY_GRAPH.sync_order():
            config = MODEL_CONFIG[label]

            for key, record in engine._storage._records[label].items():
                data = {}

                for field_name in config.fields:
                    if field_name in record.data:
                        data[field_name] = _coerce_value(record.data[field_name])

                for foreign_key in config.foreign_key_fields:
                    if foreign_key in record.data:
                        data[foreign_key] = record.data[foreign_key]

                config.model.objects.update_or_create(
                    pk=key,
                    defaults={
                        **data,
                        'sync_field_last_modified': max(
                            record.timestamps.values(), default=0,
                        ),
                        'sync_field_timestamps': dict(record.timestamps),
                    },
                )

    def _serialize_result(self, result: Any) -> SerializedSyncResult:
        return SerializedSyncResult(
            applied={
                label: [str(key) for key in keys]
                for label, keys in result.applied.items()
            },
            compatible={
                label: [str(key) for key in keys]
                for label, keys in result.compatible.items()
            },
            conflict_log=[
                ConflictLogEntry(
                    field_conflicts=[
                        FieldConflictDetail(
                            field_name=field_conflict.field_name,
                            local_timestamp=field_conflict.local_timestamp,
                            local_value=field_conflict.local_value,
                            remote_timestamp=field_conflict.remote_timestamp,
                            remote_value=field_conflict.remote_value,
                            winner=self._determine_winner(
                                str(entry.resolution_source),
                                {
                                    'local_timestamp': field_conflict.local_timestamp,
                                    'remote_timestamp': field_conflict.remote_timestamp,
                                },
                            ),
                        )
                        for field_conflict in entry.conflict.field_conflicts
                    ],
                    key=str(entry.conflict.key),
                    model_label=entry.conflict.model_label,
                    resolution_source=str(entry.resolution_source),
                )
                for entry in result.conflict_log
            ],
            conflicts={
                label: [str(key) for key in keys]
                for label, keys in result.conflicts.items()
            },
            created={
                label: [str(key) for key in keys]
                for label, keys in result.created.items()
            },
            deleted={
                label: [str(key) for key in keys]
                for label, keys in result.deleted.items()
            },
            errors=list(result.errors) if hasattr(result, 'errors') else [],
            skipped={
                label: [str(key) for key in keys]
                for label, keys in result.skipped.items()
            },
        )

    def _sync_tablet(
        self,
        clock: HybridLogicalClock,
        tablet_database: str,
        strategy: str,
    ) -> TabletSyncData:
        tablet_resolver, cloud_resolver = self._build_resolvers(strategy)

        tablet_engine = self._build_engine(clock, tablet_database, tablet_resolver)
        cloud_engine = self._build_engine(clock, 'cloud', cloud_resolver)

        tablet_record_count = self._load_from_orm(tablet_engine, tablet_database)
        cloud_record_count = self._load_from_orm(cloud_engine, 'cloud')

        tablet_checkpoint = tablet_engine._storage.get_checkpoint(tablet_database)
        cloud_checkpoint = cloud_engine._storage.get_checkpoint('cloud')

        tablet_manifest = tablet_engine._collect(tablet_checkpoint)
        cloud_manifest = cloud_engine._collect(cloud_checkpoint)

        tablet_manifest.checksum = tablet_manifest.compute_checksum()
        cloud_manifest.checksum = cloud_manifest.compute_checksum()

        tablet_response, tablet_result = cloud_engine.process(tablet_manifest)
        cloud_response, cloud_result = tablet_engine.process(cloud_manifest)

        self._apply_response(tablet_engine, cloud_response)
        self._apply_response(cloud_engine, tablet_response)

        tablet_engine._storage.save_checkpoint(tablet_database, cloud_response.checkpoint)
        cloud_engine._storage.save_checkpoint('cloud', tablet_response.checkpoint)

        self._persist_to_orm(tablet_engine, tablet_database)
        self._persist_to_orm(cloud_engine, 'cloud')

        return TabletSyncData(
            cloud_record_count=cloud_record_count,
            cloud_result=self._serialize_result(cloud_result),
            tablet_record_count=tablet_record_count,
            tablet_result=self._serialize_result(tablet_result),
        )
