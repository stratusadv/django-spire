from __future__ import annotations

import logging

from typing import Any

from django_spire.contrib.sync.core.clock import HybridLogicalClock
from django_spire.contrib.sync.database.engine import DatabaseEngine
from django_spire.contrib.sync.database.graph import DependencyGraph
from django_spire.contrib.sync.database.manifest import SyncManifest
from django_spire.contrib.sync.database.record import SyncRecord
from django_spire.contrib.sync.database.storage import DatabaseSyncStorage


logger = logging.getLogger(__name__)

MODEL = 'app.TestModel'


class InMemoryDatabaseStorage(DatabaseSyncStorage):
    def __init__(self, models: list[str]) -> None:
        self._checkpoints: dict[str, int] = {}
        self._models = sorted(models)
        self._records: dict[str, dict[str, SyncRecord]] = {
            m: {} for m in models
        }

    def seed(
        self,
        model_label: str,
        key: str,
        data: dict[str, Any],
        timestamps: dict[str, int],
    ) -> None:
        clean = {k: v for k, v in data.items() if k != 'sync_field_timestamps'}

        self._records[model_label][key] = SyncRecord(
            key=key,
            data=dict(clean),
            timestamps=dict(timestamps),
        )

    def delete_many(
        self,
        model_label: str,
        deletes: dict[str, int],
    ) -> None:
        for key, tombstone_ts in deletes.items():
            existing = self._records[model_label].get(key)

            if existing is None:
                continue

            if existing.sync_field_last_modified > tombstone_ts:
                continue

            self._records[model_label].pop(key, None)

    def get_changed_since(
        self,
        model_label: str,
        timestamp: int,
    ) -> dict[str, SyncRecord]:
        return {
            key: record
            for key, record in self._records[model_label].items()
            if record.sync_field_last_modified > timestamp
        }

    def get_checkpoint(self, node_id: str) -> int:
        return self._checkpoints.get(node_id, 0)

    def get_records(
        self,
        model_label: str,
        keys: set[str],
    ) -> dict[str, SyncRecord]:
        return {
            k: v
            for k, v in self._records[model_label].items()
            if k in keys
        }

    def get_syncable_models(self) -> list[str]:
        return list(self._models)

    def save_checkpoint(self, node_id: str, timestamp: int) -> None:
        self._checkpoints[node_id] = timestamp

    def upsert_many(
        self,
        model_label: str,
        records: dict[str, SyncRecord],
    ) -> set[str]:
        skipped: set[str] = set()

        for key, sync_record in records.items():
            existing = self._records[model_label].get(key)

            if existing is not None and sync_record.sync_field_last_modified < existing.sync_field_last_modified:
                skipped.add(key)
                continue

            if existing is None and not sync_record.timestamps:
                logger.warning(
                    'Skipping ghost record %s for %s',
                    key,
                    model_label,
                )
                skipped.add(key)
                continue

            self._records[model_label][key] = SyncRecord(
                key=key,
                data=dict(sync_record.data),
                timestamps=dict(sync_record.timestamps),
                received_at=sync_record.received_at,
            )

        return skipped


class FakeTransport:
    def __init__(self, response: SyncManifest) -> None:
        self._response = response
        self.last_manifest: SyncManifest | None = None

    def exchange(self, manifest: SyncManifest) -> SyncManifest:
        self.last_manifest = manifest
        return self._response


class DirectTransport:
    def __init__(self, server_engine: DatabaseEngine) -> None:
        self._server = server_engine
        self.exchanges: list[tuple[SyncManifest, SyncManifest]] = []

    def exchange(self, manifest: SyncManifest) -> SyncManifest:
        wire_in = SyncManifest.from_dict(manifest.to_dict())
        raw_response, _result = self._server.process(wire_in)
        wire_out = SyncManifest.from_dict(raw_response.to_dict())
        self.exchanges.append((wire_in, wire_out))
        return wire_out


SURVEY = 'survey.Survey'
STAKE = 'survey.Stake'

ALL_MODELS = [SURVEY, STAKE]

SURVEY_DEPS: dict[str, set[str]] = {
    SURVEY: set(),
    STAKE: {SURVEY},
}


class SyncHarness:
    def __init__(
        self,
        models: list[str] | None = None,
        edges: dict[str, set[str]] | None = None,
    ) -> None:
        models = models or ALL_MODELS
        edges = edges or SURVEY_DEPS

        self.clock = HybridLogicalClock()
        self.tablet_storage = InMemoryDatabaseStorage(models)
        self.server_storage = InMemoryDatabaseStorage(models)

        graph = DependencyGraph(edges)

        self.server_engine = DatabaseEngine(
            storage=self.server_storage,
            graph=graph,
            clock=self.clock,
            node_id='server',
            clock_drift_max=None,
        )

        self.transport = DirectTransport(self.server_engine)

        self.tablet_engine = DatabaseEngine(
            storage=self.tablet_storage,
            graph=graph,
            clock=self.clock,
            transport=self.transport,
            node_id='tablet',
            clock_drift_max=None,
        )

    def ts(self) -> int:
        return self.clock.now()

    def tablet_save(
        self,
        model_label: str,
        key: str,
        data: dict[str, Any],
        timestamps: dict[str, int],
    ) -> None:
        self.tablet_storage.seed(model_label, key, data, timestamps)

    def server_save(
        self,
        model_label: str,
        key: str,
        data: dict[str, Any],
        timestamps: dict[str, int],
    ) -> None:
        self.server_storage.seed(model_label, key, data, timestamps)

    def sync(self) -> None:
        self.tablet_engine.sync()

    def tablet_record(self, model_label: str, key: str) -> SyncRecord | None:
        return self.tablet_storage._records[model_label].get(key)

    def server_record(self, model_label: str, key: str) -> SyncRecord | None:
        return self.server_storage._records[model_label].get(key)
