from __future__ import annotations

from contextlib import nullcontext
from typing import Any
from unittest.mock import patch

import pytest

from django_spire.contrib.sync.core.clock import HybridLogicalClock
from django_spire.contrib.sync.database.conflict import FieldTimestampWins
from django_spire.contrib.sync.database.engine import DatabaseEngine
from django_spire.contrib.sync.database.graph import DependencyGraph
from django_spire.contrib.sync.database.reconciler import PayloadReconciler
from django_spire.contrib.sync.database.record import SyncRecord
from django_spire.contrib.sync.tests.database.helpers import (
    DirectTransport,
    InMemoryDatabaseStorage,
    MODEL,
)


def _make_storage(
    models: list[str] | None = None,
    records: dict[str, dict[str, SyncRecord]] | None = None,
) -> InMemoryDatabaseStorage:
    storage = InMemoryDatabaseStorage(models or [MODEL])

    if records:
        for model_label, model_records in records.items():
            for key, record in model_records.items():
                storage._records[model_label][key] = record

    return storage


def _make_engine(
    storage: InMemoryDatabaseStorage,
    node_id: str,
    clock: HybridLogicalClock,
    transport: Any = None,
    batch_size: int | None = None,
    batch_bytes: int | None = None,
) -> DatabaseEngine:
    models = storage.get_syncable_models()
    graph = DependencyGraph({m: set() for m in models})

    return DatabaseEngine(
        batch_bytes=batch_bytes,
        batch_size=batch_size,
        clock=clock,
        clock_drift_max=None,
        graph=graph,
        node_id=node_id,
        reconciler=PayloadReconciler(resolver=FieldTimestampWins()),
        storage=storage,
        transaction=nullcontext,
        transport=transport,
    )


def _seed_records(
    storage: InMemoryDatabaseStorage,
    count: int,
    base_ts: int = 1000,
    prefix: str = '',
) -> dict[str, SyncRecord]:
    records: dict[str, SyncRecord] = {}

    for i in range(count):
        key = f'{prefix}key-{i:04d}'
        ts = base_ts + i

        record = SyncRecord(
            key=key,
            data={'id': key, 'value': i},
            timestamps={'id': ts, 'value': ts},
        )

        storage._records[MODEL][key] = record
        records[key] = record

    return records


@pytest.fixture(autouse=True)
def _fixed_time() -> Any:
    with patch('django_spire.contrib.sync.database.engine.time') as mock_time:
        mock_time.time.return_value = 1000
        yield mock_time


class TestPaginatedPull:
    def test_fresh_tablet_gets_all_records(self) -> None:
        clock = HybridLogicalClock()

        server_storage = _make_storage()
        _seed_records(server_storage, count=100)
        server = _make_engine(server_storage, 'server', clock, batch_size=10)

        tablet_storage = _make_storage()
        transport = DirectTransport(server)
        tablet = _make_engine(tablet_storage, 'tablet', clock, transport, batch_size=10)

        tablet.sync()

        assert len(tablet_storage._records[MODEL]) == 100

    def test_all_keys_match_after_paginated_pull(self) -> None:
        clock = HybridLogicalClock()

        server_storage = _make_storage()
        seeded = _seed_records(server_storage, count=100)
        server = _make_engine(server_storage, 'server', clock, batch_size=10)

        tablet_storage = _make_storage()
        transport = DirectTransport(server)
        tablet = _make_engine(tablet_storage, 'tablet', clock, transport, batch_size=10)

        tablet.sync()

        for key in seeded:
            assert key in tablet_storage._records[MODEL]

    def test_data_matches_after_paginated_pull(self) -> None:
        clock = HybridLogicalClock()

        server_storage = _make_storage()
        _seed_records(server_storage, count=50)
        server = _make_engine(server_storage, 'server', clock, batch_size=7)

        tablet_storage = _make_storage()
        transport = DirectTransport(server)
        tablet = _make_engine(tablet_storage, 'tablet', clock, transport, batch_size=7)

        tablet.sync()

        for key in server_storage._records[MODEL]:
            server_record = server_storage._records[MODEL][key]
            tablet_record = tablet_storage._records[MODEL][key]

            assert server_record.data == tablet_record.data
            assert server_record.timestamps == tablet_record.timestamps


class TestPaginatedIdempotency:
    def test_resync_after_full_pull_is_noop(self) -> None:
        clock = HybridLogicalClock()

        server_storage = _make_storage()
        _seed_records(server_storage, count=100)
        server = _make_engine(server_storage, 'server', clock, batch_size=10)

        tablet_storage = _make_storage()
        transport = DirectTransport(server)
        tablet = _make_engine(tablet_storage, 'tablet', clock, transport, batch_size=10)

        tablet.sync()
        assert len(tablet_storage._records[MODEL]) == 100

        result = tablet.sync()

        total_applied = sum(len(keys) for keys in result.applied.values())
        total_created = sum(len(keys) for keys in result.created.values())
        total_pushed = sum(len(keys) for keys in result.pushed.values())

        assert total_applied == 0
        assert total_created == 0
        assert total_pushed == 0

    def test_timestamps_stable_across_resyncs(self) -> None:
        clock = HybridLogicalClock()

        server_storage = _make_storage()
        _seed_records(server_storage, count=50)
        server = _make_engine(server_storage, 'server', clock, batch_size=10)

        tablet_storage = _make_storage()
        transport = DirectTransport(server)
        tablet = _make_engine(tablet_storage, 'tablet', clock, transport, batch_size=10)

        tablet.sync()

        timestamps_before = {
            key: dict(record.timestamps)
            for key, record in tablet_storage._records[MODEL].items()
        }

        tablet.sync()
        tablet.sync()

        for key, ts_before in timestamps_before.items():
            ts_after = dict(tablet_storage._records[MODEL][key].timestamps)
            assert ts_before == ts_after, f'{key}: timestamps mutated on re-sync'


class TestPaginatedPush:
    def test_tablet_push_then_second_tablet_pull(self) -> None:
        clock = HybridLogicalClock()

        server_storage = _make_storage()
        server = _make_engine(server_storage, 'server', clock, batch_size=10)

        tablet_a_storage = _make_storage()
        _seed_records(tablet_a_storage, count=100)
        transport_a = DirectTransport(server)
        tablet_a = _make_engine(tablet_a_storage, 'tablet-a', clock, transport_a, batch_size=10)

        tablet_a.sync()

        tablet_b_storage = _make_storage()
        transport_b = DirectTransport(server)
        tablet_b = _make_engine(tablet_b_storage, 'tablet-b', clock, transport_b, batch_size=10)

        tablet_b.sync()

        assert len(tablet_b_storage._records[MODEL]) == 100

    def test_bidirectional_paginated_sync(self) -> None:
        clock = HybridLogicalClock()

        server_storage = _make_storage()
        _seed_records(server_storage, count=30, base_ts=1000, prefix='srv-')
        server = _make_engine(server_storage, 'server', clock, batch_size=10)

        tablet_storage = _make_storage()
        _seed_records(tablet_storage, count=30, base_ts=5000, prefix='tab-')
        transport = DirectTransport(server)
        tablet = _make_engine(tablet_storage, 'tablet', clock, transport, batch_size=10)

        tablet.sync()

        assert len(server_storage._records[MODEL]) == 60
        assert len(tablet_storage._records[MODEL]) == 60


class TestCheckpointIntegrity:
    def test_checkpoint_does_not_skip_unpaginated_records(self) -> None:
        clock = HybridLogicalClock()

        server_storage = _make_storage()
        _seed_records(server_storage, count=100)
        server = _make_engine(server_storage, 'server', clock, batch_size=10)

        tablet_storage = _make_storage()
        transport = DirectTransport(server)
        tablet = _make_engine(tablet_storage, 'tablet', clock, transport, batch_size=10)

        tablet.sync()

        missing = set(server_storage._records[MODEL]) - set(tablet_storage._records[MODEL])

        assert len(missing) == 0, f'{len(missing)} records lost to checkpoint skip'

    def test_checkpoint_advances_correctly_after_full_pull(self) -> None:
        clock = HybridLogicalClock()

        server_storage = _make_storage()
        seeded = _seed_records(server_storage, count=100)
        server = _make_engine(server_storage, 'server', clock, batch_size=10)

        tablet_storage = _make_storage()
        transport = DirectTransport(server)
        tablet = _make_engine(tablet_storage, 'tablet', clock, transport, batch_size=10)

        tablet.sync()

        checkpoint = tablet_storage.get_checkpoint('tablet')
        max_seeded_ts = max(r.sync_field_last_modified for r in seeded.values())

        assert checkpoint >= max_seeded_ts

    def test_new_records_after_full_pull_are_synced(self) -> None:
        clock = HybridLogicalClock()

        server_storage = _make_storage()
        _seed_records(server_storage, count=50)
        server = _make_engine(server_storage, 'server', clock, batch_size=10)

        tablet_storage = _make_storage()
        transport = DirectTransport(server)
        tablet = _make_engine(tablet_storage, 'tablet', clock, transport, batch_size=10)

        tablet.sync()
        assert len(tablet_storage._records[MODEL]) == 50

        new_ts = clock.now()

        server_storage._records[MODEL]['new-key'] = SyncRecord(
            key='new-key',
            data={'id': 'new-key', 'value': 999},
            timestamps={'id': new_ts, 'value': new_ts},
        )

        tablet.sync()

        assert 'new-key' in tablet_storage._records[MODEL]
        assert len(tablet_storage._records[MODEL]) == 51


class TestBatchSizeVariations:
    @pytest.mark.parametrize('batch_size', [1, 3, 7, 13, 50, 100, 200])
    def test_all_records_arrive_regardless_of_batch_size(
        self,
        batch_size: int,
    ) -> None:
        clock = HybridLogicalClock()

        server_storage = _make_storage()
        _seed_records(server_storage, count=100)
        server = _make_engine(server_storage, 'server', clock, batch_size=batch_size)

        tablet_storage = _make_storage()
        transport = DirectTransport(server)
        tablet = _make_engine(tablet_storage, 'tablet', clock, transport, batch_size=batch_size)

        tablet.sync()

        assert len(tablet_storage._records[MODEL]) == 100

    @pytest.mark.parametrize('batch_size', [1, 3, 7, 13, 50, 100, 200])
    def test_resync_is_noop_regardless_of_batch_size(
        self,
        batch_size: int,
    ) -> None:
        clock = HybridLogicalClock()

        server_storage = _make_storage()
        _seed_records(server_storage, count=100)
        server = _make_engine(server_storage, 'server', clock, batch_size=batch_size)

        tablet_storage = _make_storage()
        transport = DirectTransport(server)
        tablet = _make_engine(tablet_storage, 'tablet', clock, transport, batch_size=batch_size)

        tablet.sync()

        result = tablet.sync()

        total = (
            sum(len(k) for k in result.applied.values())
            + sum(len(k) for k in result.created.values())
        )

        assert total == 0
