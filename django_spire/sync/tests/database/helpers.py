from __future__ import annotations

import logging

from typing import Any, TYPE_CHECKING

from django_spire.sync.core.clock import HybridLogicalClock
from django_spire.sync.database.engine import DatabaseEngine
from django_spire.sync.database.graph import DependencyGraph
from django_spire.sync.database.manifest import SyncManifest
from django_spire.sync.database.record import SyncRecord
from django_spire.sync.database.storage import (
    CheckpointPosition,
    DatabaseSyncStorage,
    SequenceRange,
    UpsertResult,
)

if TYPE_CHECKING:
    from django_spire.sync.core.model import Error


logger = logging.getLogger(__name__)

MODEL = 'app.TestModel'


class _FakeSequenceAllocator:
    def __init__(self) -> None:
        self._value = 0

    def allocate(self, count: int = 1) -> SequenceRange:
        first = self._value + 1
        self._value += count
        return SequenceRange(value_first=first, value_last=self._value)

    def current(self) -> int:
        return self._value


class InMemoryDatabaseStorage(DatabaseSyncStorage):
    def __init__(self, models: list[str]) -> None:
        self._after_keys: dict[str, dict[str, Any]] = {}
        self._checkpoints: dict[str, CheckpointPosition] = {}
        self._models = sorted(models)
        self._records: dict[str, dict[str, SyncRecord]] = {m: {} for m in models}
        self._tombstones: dict[str, dict[str, tuple[int, int, str]]] = {m: {} for m in models}
        self._sequence_allocator = _FakeSequenceAllocator()

    def seed(
        self, model_label: str, key: str, data: dict[str, Any], timestamps: dict[str, int]
    ) -> None:
        clean = {k: v for k, v in data.items() if k != 'sync_field_timestamps'}

        seq = self._sequence_allocator.current() + 1
        self._sequence_allocator.allocate(1)

        self._records[model_label][key] = SyncRecord(
            key=key, data=dict(clean), timestamps=dict(timestamps), sequence=seq
        )

    def clear_tombstones(self, model_label: str, keys: set[str]) -> None:
        for key in keys:
            self._tombstones[model_label].pop(key, None)

    def delete_many(self, model_label: str, deletes: dict[str, int], origin_node: str) -> None:
        for key, tombstone_ts in deletes.items():
            existing = self._records[model_label].get(key)

            if existing is not None and existing.sync_field_last_modified > tombstone_ts:
                continue

            self._records[model_label].pop(key, None)

            seq = self._sequence_allocator.current() + 1
            self._sequence_allocator.allocate(1)

            self._tombstones[model_label][key] = (tombstone_ts, seq, origin_node)

    def get_after_keys(self, peer_node_id: str) -> dict[str, Any]:
        return self._after_keys.get(peer_node_id) or {}

    def get_changed_since(
        self,
        model_label: str,
        sequence: int,
        peer_node_id: str,
        sequence_max: int | None = None,
        limit: int | None = None,
        after_key: str | None = None,
    ) -> dict[str, SyncRecord]:
        result = {
            key: record
            for key, record in self._records[model_label].items()
            if record.sequence > sequence
        }

        if sequence_max is not None:
            result = {
                key: record for key, record in result.items() if record.sequence <= sequence_max
            }

        if peer_node_id:
            result = {
                key: record for key, record in result.items() if record.origin_node != peer_node_id
            }

        result = dict(sorted(result.items(), key=lambda item: (item[1].sequence, item[0])))

        if after_key is not None:
            filtered: dict[str, SyncRecord] = {}

            for key, record in result.items():
                if record.sequence > sequence or (record.sequence == sequence and key > after_key):
                    filtered[key] = record

            result = filtered

        if limit is not None:
            result = dict(list(result.items())[:limit])

        return result

    def get_checkpoint(self, peer_node_id: str) -> CheckpointPosition:
        return self._checkpoints.get(
            peer_node_id, CheckpointPosition(peer_sequence=0, local_sequence_pushed=0)
        )

    def get_deletes_since(
        self, model_label: str, sequence: int, peer_node_id: str, sequence_max: int | None = None
    ) -> dict[str, int]:
        result: dict[str, int] = {}

        for key, (ts, seq, origin) in self._tombstones[model_label].items():
            if seq <= sequence:
                continue

            if sequence_max is not None and seq > sequence_max:
                continue

            if peer_node_id and origin == peer_node_id:
                continue

            result[key] = ts

        return result

    def get_records(self, model_label: str, keys: set[str]) -> dict[str, SyncRecord]:
        return {k: v for k, v in self._records[model_label].items() if k in keys}

    def get_sequence_allocator(self) -> _FakeSequenceAllocator:
        return self._sequence_allocator

    def get_syncable_models(self) -> list[str]:
        return list(self._models)

    def get_tombstones(self, model_label: str, keys: set[str]) -> dict[str, int]:
        return {k: ts for k, (ts, _, _) in self._tombstones[model_label].items() if k in keys}

    def save_checkpoint(
        self,
        peer_node_id: str,
        peer_sequence: int,
        local_sequence_pushed: int,
        after_keys: dict[str, Any] | None = None,
    ) -> None:
        self._checkpoints[peer_node_id] = CheckpointPosition(
            peer_sequence=peer_sequence, local_sequence_pushed=local_sequence_pushed
        )
        self._after_keys[peer_node_id] = after_keys or {}

    def upsert_many(
        self, model_label: str, records: dict[str, SyncRecord], origin_node: str
    ) -> UpsertResult:
        skipped: set[str] = set()
        errors: list[Error] = []

        for key, sync_record in records.items():
            existing = self._records[model_label].get(key)

            if (
                existing is not None
                and sync_record.sync_field_last_modified < existing.sync_field_last_modified
            ):
                skipped.add(key)
                continue

            if existing is None and not sync_record.timestamps:
                logger.warning('Skipping ghost record %s for %s', key, model_label)
                skipped.add(key)
                continue

            seq = self._sequence_allocator.current() + 1
            self._sequence_allocator.allocate(1)

            self._records[model_label][key] = SyncRecord(
                key=key,
                data=dict(sync_record.data),
                timestamps=dict(sync_record.timestamps),
                sequence=seq,
                origin_node=origin_node,
                received_at=sync_record.received_at,
            )

        return UpsertResult(skipped=skipped, errors=errors)


class FakeTransport:
    def __init__(self, response: SyncManifest) -> None:
        self._empty = SyncManifest(
            node_id=response.node_id,
            peer_sequence=response.peer_sequence,
            local_sequence=response.local_sequence,
            node_time=response.node_time,
            payloads=[],
        )
        self._empty.checksum = self._empty.compute_checksum()
        self._response = response
        self.call_count: int = 0
        self.last_manifest: SyncManifest | None = None
        self.manifests: list[SyncManifest] = []

    def exchange(self, manifest: SyncManifest) -> SyncManifest:
        self.last_manifest = manifest
        self.manifests.append(manifest)
        self.call_count += 1

        if self.call_count == 1:
            return self._response

        return self._empty


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

SURVEY_DEPS: dict[str, set[str]] = {SURVEY: set(), STAKE: {SURVEY}}


class SyncHarness:
    def __init__(
        self, models: list[str] | None = None, edges: dict[str, set[str]] | None = None
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
            peer_node_id='server',
            clock_drift_max=None,
        )

    def ts(self) -> int:
        return self.clock.now()

    def tablet_save(
        self, model_label: str, key: str, data: dict[str, Any], timestamps: dict[str, int]
    ) -> None:
        self.tablet_storage.seed(model_label, key, data, timestamps)

    def server_save(
        self, model_label: str, key: str, data: dict[str, Any], timestamps: dict[str, int]
    ) -> None:
        self.server_storage.seed(model_label, key, data, timestamps)

    def sync(self) -> None:
        self.tablet_engine.sync()

    def tablet_record(self, model_label: str, key: str) -> SyncRecord | None:
        return self.tablet_storage._records[model_label].get(key)

    def server_record(self, model_label: str, key: str) -> SyncRecord | None:
        return self.server_storage._records[model_label].get(key)
