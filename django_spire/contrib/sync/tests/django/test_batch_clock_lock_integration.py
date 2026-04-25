from __future__ import annotations

from typing import Any
from unittest.mock import patch

import pytest

from django_spire.contrib.sync.core.clock import HybridLogicalClock
from django_spire.contrib.sync.core.enums import SyncPhase, SyncStatus
from django_spire.contrib.sync.core.exceptions import (
    BatchLimitError,
    ClockOverflowError,
    InvalidParameterError,
    SyncAbortedError,
)
from django_spire.contrib.sync.database.engine import DatabaseEngine
from django_spire.contrib.sync.database.graph import DependencyGraph
from django_spire.contrib.sync.database.record import SyncRecord
from django_spire.contrib.sync.django.storage import DjangoSyncStorage
from django_spire.contrib.sync.tests.database.fakes import FakeLock
from django_spire.contrib.sync.tests.database.helpers import (
    FakeTransport,
    InMemoryDatabaseStorage,
    MODEL,
)
from django_spire.contrib.sync.tests.factories import make_manifest
from django_spire.contrib.sync.tests.models import SyncTestModel


@pytest.fixture
def batch_storage() -> DjangoSyncStorage:
    return DjangoSyncStorage(
        models=[SyncTestModel],
        clock=HybridLogicalClock(),
        identity_field='id',
        batch_size_max=5,
    )


def test_batch_size_max_zero_raises() -> None:
    with pytest.raises(InvalidParameterError, match='batch_size_max must be >= 1'):
        DjangoSyncStorage(
            models=[SyncTestModel],
            clock=HybridLogicalClock(),
            batch_size_max=0,
        )


def test_batch_size_max_negative_raises() -> None:
    with pytest.raises(InvalidParameterError, match='batch_size_max must be >= 1'):
        DjangoSyncStorage(
            models=[SyncTestModel],
            clock=HybridLogicalClock(),
            batch_size_max=-1,
        )


@pytest.mark.django_db
def test_upsert_many_rejects_oversized_batch(
    batch_storage: DjangoSyncStorage,
) -> None:
    records = {
        f'{i:08d}-0000-0000-0000-000000000000': SyncRecord(
            key=f'{i:08d}-0000-0000-0000-000000000000',
            data={'id': f'{i:08d}-0000-0000-0000-000000000000', 'name': f'r{i}', 'value': 0},
            timestamps={'name': 100},
        )
        for i in range(6)
    }

    with pytest.raises(BatchLimitError):
        batch_storage.upsert_many('sync_tests.SyncTestModel', records)


@pytest.mark.django_db
def test_upsert_many_allows_exactly_at_limit(
    batch_storage: DjangoSyncStorage,
) -> None:
    records = {
        f'{i:08d}-0000-0000-0000-000000000001': SyncRecord(
            key=f'{i:08d}-0000-0000-0000-000000000001',
            data={'id': f'{i:08d}-0000-0000-0000-000000000001', 'name': f'r{i}', 'value': 0},
            timestamps={'name': 100, 'value': 100},
        )
        for i in range(5)
    }

    skipped = batch_storage.upsert_many('sync_tests.SyncTestModel', records)

    assert len(skipped) == 0
    assert SyncTestModel.objects.filter(
        pk__in=list(records.keys()),
    ).count() == 5


@pytest.mark.django_db
def test_delete_many_rejects_oversized_batch(
    batch_storage: DjangoSyncStorage,
) -> None:
    deletes = {
        f'{i:08d}-0000-0000-0000-000000000002': 500
        for i in range(6)
    }

    with pytest.raises(BatchLimitError):
        batch_storage.delete_many('sync_tests.SyncTestModel', deletes)


def test_clock_overflow_raises() -> None:
    clock = HybridLogicalClock()
    clock._physical = lambda: 500

    clock._last = (1000 << 16) | 0xFFFF

    with pytest.raises(ClockOverflowError, match='overflow'):
        clock.now()


@patch('django_spire.contrib.sync.database.engine.time')
def test_engine_sync_acquires_and_releases_lock(mock_time: Any) -> None:
    mock_time.time.return_value = 500

    lock = FakeLock()
    mem_storage = InMemoryDatabaseStorage([MODEL])
    graph = DependencyGraph({MODEL: set()})

    response = make_manifest(
        node_id='server', checkpoint=500, node_time=500,
    )
    transport = FakeTransport(response)

    engine = DatabaseEngine(
        storage=mem_storage,
        graph=graph,
        clock=HybridLogicalClock(),
        lock=lock,
        transport=transport,
        node_id='tablet',
        clock_drift_max=None,
    )

    engine.sync()

    assert len(lock.acquired) == 1
    assert lock.acquired[0] == 'tablet'
    assert len(lock.released) == 1
    assert lock.released[0][1] == SyncStatus.SUCCESS


@patch('django_spire.contrib.sync.database.engine.time')
def test_engine_sync_releases_lock_on_failure(mock_time: Any) -> None:
    mock_time.time.return_value = 500

    lock = FakeLock()
    mem_storage = InMemoryDatabaseStorage([MODEL])
    graph = DependencyGraph({MODEL: set()})

    response = make_manifest(
        node_id='server', checkpoint=500, node_time=9999,
    )
    transport = FakeTransport(response)

    engine = DatabaseEngine(
        storage=mem_storage,
        graph=graph,
        clock=HybridLogicalClock(),
        lock=lock,
        transport=transport,
        node_id='tablet',
        clock_drift_max=60,
    )

    with pytest.raises(SyncAbortedError, match='Clock drift'):
        engine.sync()

    assert len(lock.released) == 1
    assert lock.released[0][1] == SyncStatus.FAILURE


@patch('django_spire.contrib.sync.database.engine.time')
def test_engine_sync_reports_phases_to_lock(mock_time: Any) -> None:
    mock_time.time.return_value = 500

    lock = FakeLock()
    mem_storage = InMemoryDatabaseStorage([MODEL])
    graph = DependencyGraph({MODEL: set()})

    response = make_manifest(
        node_id='server', checkpoint=500, node_time=500,
    )
    transport = FakeTransport(response)

    engine = DatabaseEngine(
        storage=mem_storage,
        graph=graph,
        clock=HybridLogicalClock(),
        lock=lock,
        transport=transport,
        node_id='tablet',
        clock_drift_max=None,
    )

    engine.sync()

    phase_names = [phase for _, phase in lock.phases]

    assert SyncPhase.COLLECTING in phase_names
    assert SyncPhase.COMPLETE in phase_names


@patch('django_spire.contrib.sync.database.engine.time')
def test_engine_sync_without_lock_still_works(mock_time: Any) -> None:
    mock_time.time.return_value = 500

    mem_storage = InMemoryDatabaseStorage([MODEL])
    graph = DependencyGraph({MODEL: set()})

    response = make_manifest(
        node_id='server', checkpoint=500, node_time=500,
    )
    transport = FakeTransport(response)

    engine = DatabaseEngine(
        storage=mem_storage,
        graph=graph,
        clock=HybridLogicalClock(),
        transport=transport,
        node_id='tablet',
        clock_drift_max=None,
    )

    result = engine.sync()

    assert result.ok
