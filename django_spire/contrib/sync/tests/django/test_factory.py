from __future__ import annotations

import pytest

from django_spire.contrib.sync.core.clock import HybridLogicalClock
from django_spire.contrib.sync.database.conflict import RemoteWins
from django_spire.contrib.sync.database.engine import DatabaseEngine
from django_spire.contrib.sync.database.graph import DependencyGraph
from django_spire.contrib.sync.django.factory import (
    build_client_engine,
    build_server_engine,
)
from django_spire.contrib.sync.django.mixin import SyncableMixin
from django_spire.contrib.sync.django.storage import DjangoSyncStorage
from django_spire.contrib.sync.tests.models import SyncTestModel


@pytest.mark.django_db
def test_build_client_engine_returns_engine() -> None:
    clock = HybridLogicalClock()
    SyncableMixin.configure(clock)

    engine = build_client_engine(
        models=[SyncTestModel],
        node_id='tablet',
        url='https://example.com/sync/',
        headers={'Authorization': 'Bearer token'},
    )

    assert isinstance(engine, DatabaseEngine)


@pytest.mark.django_db
def test_build_client_engine_custom_clock() -> None:
    custom_clock = HybridLogicalClock()
    SyncableMixin.configure(HybridLogicalClock())

    engine = build_client_engine(
        models=[SyncTestModel],
        node_id='tablet',
        url='https://example.com/sync/',
        headers={'Authorization': 'Bearer token'},
        clock=custom_clock,
    )

    assert engine._clock is custom_clock


@pytest.mark.django_db
def test_build_client_engine_custom_resolver() -> None:
    clock = HybridLogicalClock()
    SyncableMixin.configure(clock)

    resolver = RemoteWins()

    engine = build_client_engine(
        models=[SyncTestModel],
        node_id='tablet',
        url='https://example.com/sync/',
        headers={'Authorization': 'Bearer token'},
        resolver=resolver,
    )

    assert engine._reconciler._resolver is resolver


@pytest.mark.django_db
def test_build_client_engine_custom_storage() -> None:
    clock = HybridLogicalClock()
    SyncableMixin.configure(clock)

    storage = DjangoSyncStorage(models=[SyncTestModel])

    engine = build_client_engine(
        models=[SyncTestModel],
        node_id='tablet',
        url='https://example.com/sync/',
        headers={'Authorization': 'Bearer token'},
        storage=storage,
    )

    assert engine._storage is storage


@pytest.mark.django_db
def test_build_server_engine_returns_engine() -> None:
    clock = HybridLogicalClock()
    SyncableMixin.configure(clock)

    engine = build_server_engine(
        models=[SyncTestModel],
        node_id='server',
    )

    assert isinstance(engine, DatabaseEngine)


@pytest.mark.django_db
def test_build_server_engine_has_lock_by_default() -> None:
    clock = HybridLogicalClock()
    SyncableMixin.configure(clock)

    engine = build_server_engine(
        models=[SyncTestModel],
        node_id='server',
    )

    assert engine._lock is not None


@pytest.mark.django_db
def test_build_server_engine_no_transport() -> None:
    clock = HybridLogicalClock()
    SyncableMixin.configure(clock)

    engine = build_server_engine(
        models=[SyncTestModel],
        node_id='server',
    )

    assert engine._transport is None


@pytest.mark.django_db
def test_build_server_engine_custom_graph() -> None:
    clock = HybridLogicalClock()
    SyncableMixin.configure(clock)

    label = SyncTestModel._meta.label
    graph = DependencyGraph({label: set()})

    engine = build_server_engine(
        models=[SyncTestModel],
        node_id='server',
        graph=graph,
    )

    assert engine._graph is graph
