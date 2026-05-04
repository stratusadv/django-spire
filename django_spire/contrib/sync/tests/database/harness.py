from __future__ import annotations

import random
import string

from dataclasses import dataclass, field
from typing import Any, TYPE_CHECKING

from django_spire.contrib.sync.core.clock import HybridLogicalClock
from django_spire.contrib.sync.database.conflict import (
    ConflictResolver,
    FieldTimestampWins,
)
from django_spire.contrib.sync.database.engine import DatabaseEngine
from django_spire.contrib.sync.database.graph import DependencyGraph
from django_spire.contrib.sync.database.manifest import SyncManifest
from django_spire.contrib.sync.database.reconciler import PayloadReconciler
from django_spire.contrib.sync.tests.database.helpers import InMemoryDatabaseStorage

if TYPE_CHECKING:
    from django_spire.contrib.sync.database.record import SyncRecord


@dataclass
class ModelSchema:
    label: str
    fields: list[str]
    dependencies: set[str] = field(default_factory=set)


@dataclass
class TabletSnapshot:
    tablet_id: str
    records: dict[str, dict[str, SyncRecord]]


@dataclass
class SyncCycleResult:
    tablet_id: str
    pushed: dict[str, list[str]]
    applied: dict[str, list[str]]
    conflicts: dict[str, list[str]]
    errors: list[Any]
    ok: bool


class MultiTabletTransport:
    def __init__(self, server_engine: DatabaseEngine) -> None:
        self._server = server_engine
        self.exchanges: list[tuple[str, SyncManifest, SyncManifest]] = []

    def exchange(self, manifest: SyncManifest) -> SyncManifest:
        wire_in = SyncManifest.from_dict(manifest.to_dict())
        raw_response, _result = self._server.process(wire_in)
        wire_out = SyncManifest.from_dict(raw_response.to_dict())
        self.exchanges.append((manifest.node_id, wire_in, wire_out))
        return wire_out


class MultiTabletHarness:
    def __init__(
        self,
        tablet_count: int = 2,
        schemas: list[ModelSchema] | None = None,
        resolver: ConflictResolver | None = None,
        seed: int | None = None,
    ) -> None:
        self.rng = random.Random(seed)
        self.clock = HybridLogicalClock()

        if schemas is None:
            schemas = [
                ModelSchema(label='app.Parent', fields=['name', 'value']),
                ModelSchema(
                    label='app.Child',
                    fields=['x', 'y', 'is_active'],
                    dependencies={'app.Parent'},
                ),
            ]

        self.schemas = {s.label: s for s in schemas}
        self.model_labels = sorted(self.schemas.keys())
        self.edges = {s.label: s.dependencies for s in schemas}
        self.graph = DependencyGraph(self.edges)

        resolver = resolver or FieldTimestampWins()

        self.server_storage = InMemoryDatabaseStorage(self.model_labels)
        self.server_engine = DatabaseEngine(
            storage=self.server_storage,
            graph=self.graph,
            clock=self.clock,
            node_id='server',
            clock_drift_max=None,
            reconciler=PayloadReconciler(resolver=resolver),
        )

        self.transport = MultiTabletTransport(self.server_engine)

        self.tablet_storages: dict[str, InMemoryDatabaseStorage] = {}
        self.tablet_engines: dict[str, DatabaseEngine] = {}

        for i in range(1, tablet_count + 1):
            tablet_id = f'tablet_{i}'
            storage = InMemoryDatabaseStorage(self.model_labels)
            engine = DatabaseEngine(
                storage=storage,
                graph=self.graph,
                clock=self.clock,
                transport=self.transport,
                node_id=tablet_id,
                clock_drift_max=None,
                reconciler=PayloadReconciler(resolver=resolver),
            )
            self.tablet_storages[tablet_id] = storage
            self.tablet_engines[tablet_id] = engine

    @property
    def tablet_ids(self) -> list[str]:
        return list(self.tablet_engines.keys())

    def ts(self) -> int:
        return self.clock.now()

    def tablet_save(
        self,
        tablet_id: str,
        model_label: str,
        key: str,
        data: dict[str, Any],
        timestamps: dict[str, int],
    ) -> None:
        self.tablet_storages[tablet_id].seed(model_label, key, data, timestamps)

    def server_save(
        self,
        model_label: str,
        key: str,
        data: dict[str, Any],
        timestamps: dict[str, int],
    ) -> None:
        self.server_storage.seed(model_label, key, data, timestamps)

    def sync_tablet(self, tablet_id: str) -> None:
        self.tablet_engines[tablet_id].sync()

    def sync_all(self) -> None:
        for tablet_id in self.tablet_ids:
            self.sync_tablet(tablet_id)

    def sync_all_converge(self, rounds: int = 2) -> None:
        for _ in range(rounds):
            self.sync_all()

    def tablet_record(
        self,
        tablet_id: str,
        model_label: str,
        key: str,
    ) -> SyncRecord | None:
        return self.tablet_storages[tablet_id]._records[model_label].get(key)

    def server_record(
        self,
        model_label: str,
        key: str,
    ) -> SyncRecord | None:
        return self.server_storage._records[model_label].get(key)

    def all_tablet_records(
        self,
        model_label: str,
    ) -> dict[str, dict[str, SyncRecord]]:
        return {
            tablet_id: dict(storage._records[model_label])
            for tablet_id, storage in self.tablet_storages.items()
        }

    def server_records(self, model_label: str) -> dict[str, SyncRecord]:
        return dict(self.server_storage._records[model_label])

    def generate_record(
        self,
        model_label: str,
        key: str,
        ts: int | None = None,
    ) -> tuple[dict[str, Any], dict[str, int]]:
        if ts is None:
            ts = self.ts()

        schema = self.schemas[model_label]
        data: dict[str, Any] = {'id': key}
        timestamps: dict[str, int] = {}

        for field_name in schema.fields:
            data[field_name] = self._random_value(field_name)
            timestamps[field_name] = ts

        return data, timestamps

    def seed_records(
        self,
        model_label: str,
        count: int,
        target: str = 'server',
        key_prefix: str = '',
    ) -> list[str]:
        keys = []

        for i in range(count):
            key = f'{key_prefix}{model_label.rsplit(".", maxsplit=1)[-1].lower()}-{i}'
            data, timestamps = self.generate_record(model_label, key)
            keys.append(key)

            if target == 'server':
                self.server_save(model_label, key, data, timestamps)
            else:
                self.tablet_save(target, model_label, key, data, timestamps)

        return keys

    def assert_converged(self, model_label: str | None = None) -> None:
        labels = [model_label] if model_label else self.model_labels

        for label in labels:
            server_keys = set(self.server_storage._records[label].keys())

            for tablet_id in self.tablet_ids:
                tablet_keys = set(
                    self.tablet_storages[tablet_id]._records[label].keys()
                )

                assert tablet_keys == server_keys, (
                    f'{tablet_id} key mismatch for {label}: '
                    f'tablet_only={tablet_keys - server_keys} '
                    f'server_only={server_keys - tablet_keys}'
                )

                for key in server_keys:
                    tablet_rec = self.tablet_record(tablet_id, label, key)
                    server_rec = self.server_record(label, key)

                    assert tablet_rec.data == server_rec.data, (
                        f'{tablet_id}:{label}:{key} data mismatch: '
                        f'tablet={tablet_rec.data} server={server_rec.data}'
                    )

    def run_random_operations(
        self,
        model_label: str,
        num_operations: int,
        num_keys: int = 5,
        sync_probability: float = 0.2,
    ) -> None:
        keys = [f'r-{i}' for i in range(num_keys)]

        for _ in range(num_operations):
            roll = self.rng.random()

            if roll < sync_probability:
                tablet_id = self.rng.choice(self.tablet_ids)
                self.sync_tablet(tablet_id)
            else:
                side = self.rng.choice([*self.tablet_ids, 'server'])
                key = self.rng.choice(keys)
                ts = self.ts()
                schema = self.schemas[model_label]

                fields_to_update = self.rng.sample(
                    schema.fields,
                    k=self.rng.randint(1, len(schema.fields)),
                )

                storage = (
                    self.server_storage if side == 'server'
                    else self.tablet_storages[side]
                )

                existing = storage._records[model_label].get(key)

                if existing is not None:
                    data = dict(existing.data)
                    timestamps = dict(existing.timestamps)
                else:
                    data = {'id': key}
                    timestamps = {}

                for field_name in fields_to_update:
                    data[field_name] = self._random_value(field_name)
                    timestamps[field_name] = ts

                if side == 'server':
                    self.server_save(model_label, key, data, timestamps)
                else:
                    self.tablet_save(side, model_label, key, data, timestamps)

    def _random_value(self, field_name: str) -> Any:
        if field_name.startswith('is_'):
            return self.rng.choice([True, False])

        if any(
            field_name.endswith(suffix)
            for suffix in ('latitude', 'longitude', 'x', 'y')
        ):
            return round(self.rng.uniform(-180.0, 180.0), 6)

        if field_name in ('value', 'count', 'elevation', 'spacing'):
            return self.rng.randint(0, 1000)

        return ''.join(
            self.rng.choices(string.ascii_lowercase, k=self.rng.randint(3, 10))
        )
