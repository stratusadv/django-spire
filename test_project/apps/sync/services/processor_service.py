from __future__ import annotations

from decimal import Decimal
from typing import Any

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

from test_project.apps.sync import models
from test_project.apps.sync.config import (
    TABLET_COUNT_DEFAULT,
    get_active_tablet_databases,
)
from test_project.apps.sync.context import switch_db


MODEL_LABELS = [
    'sync.Client',
    'sync.Site',
    'sync.SurveyPlan',
    'sync.Stake',
]

MODEL_CONFIG = {
    'sync.Client': {
        'model': models.Client,
        'fields': ('name', 'contact_name', 'contact_email'),
        'fk_fields': (),
    },
    'sync.Site': {
        'model': models.Site,
        'fields': ('name', 'description', 'region', 'status'),
        'fk_fields': ('client_id',),
    },
    'sync.SurveyPlan': {
        'model': models.SurveyPlan,
        'fields': (
            'plan_number',
            'stake_spacing_m', 'line_direction', 'headland_offset_m', 'office_notes',
            'baseline_a_latitude', 'baseline_a_longitude',
            'baseline_b_latitude', 'baseline_b_longitude',
            'heading_degrees', 'crew_notes',
            'status',
        ),
        'fk_fields': ('site_id',),
    },
    'sync.Stake': {
        'model': models.Stake,
        'fields': (
            'latitude', 'longitude', 'elevation', 'is_placed',
            'stake_type', 'label',
        ),
        'fk_fields': ('survey_plan_id',),
    },
}

GRAPH = DependencyGraph({
    'sync.Client': set(),
    'sync.Site': {'sync.Client'},
    'sync.SurveyPlan': {'sync.Site'},
    'sync.Stake': {'sync.SurveyPlan'},
})

CREW_FIELDS = {
    'baseline_a_latitude',
    'baseline_a_longitude',
    'baseline_b_latitude',
    'baseline_b_longitude',
    'crew_notes',
    'elevation',
    'heading_degrees',
    'is_placed',
    'latitude',
    'longitude',
}

OFFICE_FIELDS = {
    'headland_offset_m',
    'label',
    'line_direction',
    'office_notes',
    'stake_spacing_m',
    'stake_type',
    'status',
}

STRATEGY_CHOICES = [
    ('field_ownership', 'Field Ownership'),
    ('field_timestamp_wins', 'Field Timestamp Wins'),
    ('local_wins', 'Local Wins'),
    ('remote_wins', 'Cloud Wins'),
]

DEFAULT_STRATEGY = 'field_timestamp_wins'


def _coerce_value(value: Any) -> Any:
    if isinstance(value, Decimal):
        return float(value)
    return value


class SyncProcessorService:
    def __init__(self) -> None:
        self.clock = HybridLogicalClock()

    def perform_sync(
            self,
            strategy: str = DEFAULT_STRATEGY,
            tablet_count: int = TABLET_COUNT_DEFAULT,
            tablet_dbs: list[str] | None = None,
        ) -> dict[str, Any]:
            if tablet_dbs is None:
                tablet_dbs = get_active_tablet_databases(tablet_count)

            tablet_results: dict[str, dict[str, Any]] = {}

            for tablet_db in tablet_dbs:
                tablet_result = self._sync_tablet(tablet_db, strategy)
                tablet_results[tablet_db] = tablet_result

            if len(tablet_dbs) > 1:
                for tablet_db in tablet_dbs:
                    convergence_result = self._sync_tablet(tablet_db, strategy)
                    tablet_results[tablet_db] = self._merge_results(
                        tablet_results[tablet_db], convergence_result,
                    )

            return {
                'strategy': strategy,
                'tablet_count': tablet_count,
                'tablets': tablet_results,
                'sync_order': GRAPH.sync_order(),
            }

    def _merge_results(
        self,
        first: dict[str, Any],
        second: dict[str, Any],
    ) -> dict[str, Any]:
        merged = dict(first)
        merged['cloud_record_count'] = second['cloud_record_count']

        for category in ('created', 'applied', 'conflicts', 'compatible', 'deleted', 'skipped'):
            first_data = first['tablet_result'].get(category, {})
            second_data = second['tablet_result'].get(category, {})
            combined: dict[str, list[str]] = {}

            for label in set(first_data) | set(second_data):
                keys = list(dict.fromkeys(
                    first_data.get(label, []) + second_data.get(label, [])
                ))
                combined[label] = keys

            merged['tablet_result'][category] = combined

        merged['tablet_result']['errors'] = (
            first['tablet_result'].get('errors', [])
            + second['tablet_result'].get('errors', [])
        )
        merged['tablet_result']['conflict_log'] = (
            first['tablet_result'].get('conflict_log', [])
            + second['tablet_result'].get('conflict_log', [])
        )

        return merged

    def _sync_tablet(
        self,
        tablet_db: str,
        strategy: str,
    ) -> dict[str, Any]:
        tablet_resolver, cloud_resolver = self._build_resolvers(strategy)

        tablet_engine = self._build_engine(tablet_db, tablet_resolver)
        cloud_engine = self._build_engine('cloud', cloud_resolver)

        tablet_record_count = self._load_from_orm(tablet_engine, tablet_db)
        cloud_record_count = self._load_from_orm(cloud_engine, 'cloud')

        tablet_checkpoint = tablet_engine._storage.get_checkpoint(tablet_db)
        cloud_checkpoint = cloud_engine._storage.get_checkpoint('cloud')

        tablet_manifest = tablet_engine._collect(tablet_checkpoint)
        cloud_manifest = cloud_engine._collect(cloud_checkpoint)

        tablet_manifest.checksum = tablet_manifest.compute_checksum()
        cloud_manifest.checksum = cloud_manifest.compute_checksum()

        tablet_response, tablet_result = cloud_engine.process(tablet_manifest)
        cloud_response, cloud_result = tablet_engine.process(cloud_manifest)

        self._apply_response(tablet_engine, cloud_response)
        self._apply_response(cloud_engine, tablet_response)

        tablet_engine._storage.save_checkpoint(tablet_db, cloud_response.checkpoint)
        cloud_engine._storage.save_checkpoint('cloud', tablet_response.checkpoint)

        self._persist_to_orm(tablet_engine, tablet_db)
        self._persist_to_orm(cloud_engine, 'cloud')

        return {
            'tablet_record_count': tablet_record_count,
            'cloud_record_count': cloud_record_count,
            'tablet_manifest': self._manifest_to_dict(tablet_manifest),
            'cloud_manifest': self._manifest_to_dict(cloud_manifest),
            'tablet_result': self._result_to_dict(tablet_result),
            'cloud_result': self._result_to_dict(cloud_result),
        }

    def _apply_response(self, engine: DatabaseEngine, response) -> None:
        for payload in response.payloads:
            if payload.records:
                engine._storage.upsert_many(payload.model_label, payload.records)
            if payload.deletes:
                engine._storage.delete_many(payload.model_label, payload.deletes)

    def _build_engine(
        self,
        node_id: str,
        resolver: ConflictResolver,
    ) -> DatabaseEngine:
        return DatabaseEngine(
            storage=InMemoryDatabaseStorage(MODEL_LABELS),
            graph=GRAPH,
            clock=self.clock,
            node_id=node_id,
            clock_drift_max=None,
            reconciler=PayloadReconciler(resolver=resolver),
        )

    def _build_resolvers(
        self,
        strategy: str,
    ) -> tuple[ConflictResolver, ConflictResolver]:
        if strategy == 'field_ownership':
            local_resolver = FieldOwnershipWins(
                local_fields=CREW_FIELDS,
                remote_fields=OFFICE_FIELDS,
            )
            cloud_resolver = FieldOwnershipWins(
                local_fields=OFFICE_FIELDS,
                remote_fields=CREW_FIELDS,
            )
            return local_resolver, cloud_resolver

        if strategy == 'local_wins':
            return LocalWins(), RemoteWins()

        if strategy == 'remote_wins':
            return RemoteWins(), LocalWins()

        return FieldTimestampWins(), FieldTimestampWins()

    def _determine_winner(self, resolution_source: str, fc: dict) -> str:
        if resolution_source == 'merged':
            return 'remote' if fc['remote_timestamp'] > fc['local_timestamp'] else 'local'

        if resolution_source == 'remote':
            return 'remote'

        return 'local'

    def _load_from_orm(self, engine: DatabaseEngine, db_name: str) -> int:
        switch_db(db_name)
        count = 0

        for label, config in MODEL_CONFIG.items():
            model_cls = config['model']
            fields = config['fields']
            fk_fields = config['fk_fields']

            for obj in model_cls.objects.all():
                record = {'id': str(obj.id)}

                for field in fields:
                    record[field] = _coerce_value(getattr(obj, field))

                for field in fk_fields:
                    val = getattr(obj, field)
                    record[field] = str(val) if val is not None else None

                timestamps = obj.sync_field_timestamps or {}

                if not timestamps:
                    ts = self.clock.now()
                    timestamps = dict.fromkeys(record, ts)

                engine._storage.seed(label, str(obj.id), record, timestamps)
                count += 1

        return count

    def _manifest_to_dict(self, manifest) -> dict[str, Any]:
        return {
            'node_id': manifest.node_id,
            'checkpoint': manifest.checkpoint,
            'checksum': manifest.checksum,
            'payload_counts': {
                p.model_label: len(p.records) for p in manifest.payloads
            },
        }

    def _persist_to_orm(self, engine: DatabaseEngine, db_name: str) -> None:
        switch_db(db_name)

        for label in GRAPH.sync_order():
            config = MODEL_CONFIG[label]
            model_cls = config['model']
            all_fields = list(config['fields']) + list(config['fk_fields'])

            records = engine._storage.get_changed_since(label, 0)

            if not records:
                continue

            for key, sync_record in records.items():
                defaults = {
                    f: sync_record.data[f]
                    for f in all_fields
                    if f in sync_record.data
                }

                with sync_bypass():
                    obj, _ = model_cls.objects.update_or_create(
                        id=key,
                        defaults=defaults,
                    )

                    obj.sync_field_timestamps = sync_record.timestamps
                    obj.sync_field_last_modified = sync_record.sync_field_last_modified
                    obj.save(update_fields=['sync_field_timestamps', 'sync_field_last_modified'])

    def _result_to_dict(self, result: Any) -> dict[str, Any]:
        return {
            'created': dict(result.created),
            'applied': dict(result.applied),
            'conflicts': dict(result.conflicts),
            'compatible': dict(result.compatible),
            'deleted': dict(result.deleted),
            'skipped': dict(result.skipped),
            'errors': [
                {'key': e.key, 'message': e.message}
                for e in result.errors
            ],
            'conflict_log': [
                {
                    'key': entry.conflict.key,
                    'model_label': entry.conflict.model_label,
                    'conflict_type': str(entry.conflict.conflict_type),
                    'resolution_source': str(entry.resolution_source),
                    'field_conflicts': [
                        {
                            'field_name': fc.field_name,
                            'local_value': fc.local_value,
                            'remote_value': fc.remote_value,
                            'local_timestamp': fc.local_timestamp,
                            'remote_timestamp': fc.remote_timestamp,
                            'winner': self._determine_winner(
                                str(entry.resolution_source),
                                {
                                    'remote_timestamp': fc.remote_timestamp,
                                    'local_timestamp': fc.local_timestamp,
                                },
                            ),
                        }
                        for fc in entry.conflict.field_conflicts
                    ],
                }
                for entry in result.conflict_log
            ],
        }
