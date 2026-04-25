from __future__ import annotations

from typing import Any
from unittest.mock import patch

import pytest

from django_spire.contrib.sync.core.clock import HybridLogicalClock
from django_spire.contrib.sync.core.exceptions import (
    ManifestFieldError,
    SyncAbortedError,
    TransportRequiredError,
)
from django_spire.contrib.sync.database.conflict import (
    RecordConflict,
    RecordResolution,
    RemoteWins,
)
from django_spire.contrib.sync.database.engine import DatabaseEngine
from django_spire.contrib.sync.database.graph import DependencyGraph
from django_spire.contrib.sync.database.manifest import (
    ModelPayload,
    SyncManifest,
)
from django_spire.contrib.sync.database.reconciler import PayloadReconciler
from django_spire.contrib.sync.database.record import SyncRecord

from django_spire.contrib.sync.tests.database.helpers import (
    FakeTransport,
    InMemoryDatabaseStorage,
    MODEL,
)
from django_spire.contrib.sync.tests.factories import make_manifest, make_record


class _MutatingTransport:
    def __init__(
        self,
        response: SyncManifest,
        storage: InMemoryDatabaseStorage,
        mutation: Any,
    ) -> None:
        self._response = response
        self._storage = storage
        self._mutation = mutation

        if not self._response.checksum:
            self._response.checksum = self._response.compute_checksum()

        self.last_manifest: SyncManifest | None = None

    def exchange(self, manifest: SyncManifest) -> SyncManifest:
        self.last_manifest = manifest
        self._mutation(self._storage)
        return self._response


def _make_engine(
    storage: InMemoryDatabaseStorage,
    transport: Any | None = None,
    node_id: str = 'tablet',
    clock_drift_max: int | None = None,
    **kwargs: Any,
) -> DatabaseEngine:
    models = storage.get_syncable_models()
    graph = DependencyGraph({m: set() for m in models})

    return DatabaseEngine(
        storage=storage,
        graph=graph,
        clock=kwargs.pop('clock', HybridLogicalClock()),
        transport=transport,
        node_id=node_id,
        clock_drift_max=clock_drift_max,
        **kwargs,
    )


def test_process_creates_new_record(
    storage: InMemoryDatabaseStorage,
) -> None:
    engine = _make_engine(storage, node_id='server')

    incoming = make_manifest(
        node_id='tablet',
        payloads=[
            ModelPayload(
                model_label=MODEL,
                records={
                    '1': make_record('1', {'id': '1', 'name': 'Alice'}, {'name': 200}),
                },
            ),
        ],
    )

    _, result = engine.process(incoming)

    assert '1' in result.created.get(MODEL, [])
    assert '1' in storage._records[MODEL]
    assert storage._records[MODEL]['1'].data['name'] == 'Alice'


def test_process_applies_when_local_unchanged(
    storage: InMemoryDatabaseStorage,
) -> None:
    storage.seed(MODEL, '1', {'id': '1', 'name': 'old'}, {'name': 50})

    engine = _make_engine(storage, node_id='server')

    incoming = make_manifest(
        node_id='tablet',
        checkpoint=100,
        payloads=[
            ModelPayload(
                model_label=MODEL,
                records={
                    '1': make_record('1', {'id': '1', 'name': 'new'}, {'name': 200}),
                },
            ),
        ],
    )

    _response, result = engine.process(incoming)

    assert '1' in result.applied.get(MODEL, [])
    assert storage._records[MODEL]['1'].data['name'] == 'new'


def test_process_detects_conflict_when_local_changed(
    storage: InMemoryDatabaseStorage,
) -> None:
    storage.seed(MODEL, '1', {'id': '1', 'name': 'local'}, {'name': 150})

    engine = _make_engine(storage, node_id='server')

    incoming = make_manifest(
        node_id='tablet',
        checkpoint=100,
        payloads=[
            ModelPayload(
                model_label=MODEL,
                records={
                    '1': make_record('1', {'id': '1', 'name': 'remote'}, {'name': 200}),
                },
            ),
        ],
    )

    _response, result = engine.process(incoming)

    assert '1' in result.conflicts.get(MODEL, [])


def test_process_compatible_merge_not_in_conflicts(
    storage: InMemoryDatabaseStorage,
) -> None:
    storage.seed(
        MODEL, '1',
        {'id': '1', 'name': 'local', 'value': 10},
        {'name': 150, 'value': 50},
    )

    engine = _make_engine(storage, node_id='server')

    incoming = make_manifest(
        node_id='tablet',
        checkpoint=100,
        payloads=[
            ModelPayload(
                model_label=MODEL,
                records={
                    '1': make_record(
                        '1',
                        {'id': '1', 'name': 'local', 'value': 20},
                        {'name': 50, 'value': 200},
                    ),
                },
            ),
        ],
    )

    _response, result = engine.process(incoming)

    assert '1' not in result.conflicts.get(MODEL, [])
    assert '1' in result.compatible.get(MODEL, [])


def test_process_conflict_uses_resolver(
    storage: InMemoryDatabaseStorage,
) -> None:
    storage.seed(MODEL, '1', {'id': '1', 'name': 'local'}, {'name': 150})

    engine = _make_engine(
        storage,
        node_id='server',
        reconciler=PayloadReconciler(resolver=RemoteWins()),
    )

    incoming = make_manifest(
        node_id='tablet',
        checkpoint=100,
        payloads=[
            ModelPayload(
                model_label=MODEL,
                records={
                    '1': make_record('1', {'id': '1', 'name': 'remote'}, {'name': 200}),
                },
            ),
        ],
    )

    _response, _result = engine.process(incoming)
    assert storage._records[MODEL]['1'].data['name'] == 'remote'


def test_process_deletes_unchanged_record(
    storage: InMemoryDatabaseStorage,
) -> None:
    storage.seed(MODEL, '1', {'id': '1', 'name': 'Alice'}, {'name': 50})

    engine = _make_engine(storage, node_id='server')

    incoming = make_manifest(
        node_id='tablet',
        checkpoint=100,
        payloads=[
            ModelPayload(model_label=MODEL, deletes={'1': 100}),
        ],
    )

    _response, result = engine.process(incoming)

    assert '1' in result.deleted.get(MODEL, [])
    assert '1' not in storage._records[MODEL]


def test_process_delete_conflict_local_changed(
    storage: InMemoryDatabaseStorage,
) -> None:
    storage.seed(MODEL, '1', {'id': '1', 'name': 'modified'}, {'name': 150})

    engine = _make_engine(storage, node_id='server')

    incoming = make_manifest(
        node_id='tablet',
        checkpoint=100,
        payloads=[
            ModelPayload(model_label=MODEL, deletes={'1': 100}),
        ],
    )

    _response, result = engine.process(incoming)

    assert '1' in storage._records[MODEL]
    assert '1' in result.conflicts.get(MODEL, [])


def test_process_delete_nonexistent_is_noop(
    storage: InMemoryDatabaseStorage,
) -> None:
    engine = _make_engine(storage, node_id='server')

    incoming = make_manifest(
        node_id='tablet',
        payloads=[
            ModelPayload(model_label=MODEL, deletes={'999': 999}),
        ],
    )

    _response, result = engine.process(incoming)

    assert result.ok
    assert not result.deleted.get(MODEL, [])


def test_manifest_rejects_key_in_both_records_and_deletes() -> None:
    data = {
        'node_id': 'tablet',
        'checkpoint': 0,
        'node_time': 0,
        'payloads': [
            {
                'model_label': MODEL,
                'records': {
                    '1': {'data': {'id': '1'}, 'timestamps': {'x': 1}},
                },
                'deletes': {'1': 200},
            },
        ],
    }

    with pytest.raises(ManifestFieldError, match='both'):
        SyncManifest.from_dict(data)


def test_process_includes_local_only_changes(
    storage: InMemoryDatabaseStorage,
) -> None:
    storage.seed(MODEL, '99', {'id': '99', 'name': 'local-only'}, {'name': 150})

    engine = _make_engine(storage, node_id='server')

    incoming = make_manifest(
        node_id='tablet',
        checkpoint=100,
        payloads=[
            ModelPayload(
                model_label=MODEL,
                records={
                    '1': make_record('1', {'id': '1', 'name': 'remote'}, {'name': 200}),
                },
            ),
        ],
    )

    response, _result = engine.process(incoming)

    response_keys: set[str] = set()

    for payload in response.payloads:
        if payload.model_label == MODEL:
            response_keys.update(payload.records.keys())

    assert '99' in response_keys


def test_process_includes_unreferenced_models(
    storage: InMemoryDatabaseStorage,
) -> None:
    _ = storage

    other_model = 'app.OtherModel'
    multi_storage = InMemoryDatabaseStorage([MODEL, other_model])
    multi_storage.seed(
        other_model, '50',
        {'id': '50', 'name': 'other'},
        {'name': 150},
    )

    engine = _make_engine(multi_storage, node_id='server')

    incoming = make_manifest(
        node_id='tablet',
        checkpoint=100,
        payloads=[
            ModelPayload(
                model_label=MODEL,
                records={
                    '1': make_record('1', {'id': '1', 'name': 'Alice'}, {'name': 200}),
                },
            ),
        ],
    )

    response, _result = engine.process(incoming)

    response_labels = {p.model_label for p in response.payloads}

    assert other_model in response_labels


def test_process_returns_checkpoint(
    storage: InMemoryDatabaseStorage,
) -> None:
    engine = _make_engine(storage, node_id='server')

    incoming = make_manifest(node_id='tablet')

    response, _result = engine.process(incoming)

    assert response.checkpoint > 0


def test_process_resolver_error_recorded(
    storage: InMemoryDatabaseStorage,
) -> None:
    storage.seed(MODEL, '1', {'id': '1', 'name': 'local'}, {'name': 150})

    class ExplodingResolver:
        def resolve(self, conflict: RecordConflict) -> RecordResolution:
            _ = conflict

            message = 'boom'
            raise RuntimeError(message)

    engine = _make_engine(
        storage,
        node_id='server',
        reconciler=PayloadReconciler(resolver=ExplodingResolver()),
    )

    incoming = make_manifest(
        node_id='tablet',
        checkpoint=100,
        payloads=[
            ModelPayload(
                model_label=MODEL,
                records={
                    '1': make_record('1', {'id': '1', 'name': 'remote'}, {'name': 200}),
                },
            ),
        ],
    )

    _response, result = engine.process(incoming)

    assert not result.ok
    assert any(e.key == '1' for e in result.errors)


def test_process_rejects_missing_checksum(
    storage: InMemoryDatabaseStorage,
) -> None:
    engine = _make_engine(storage, node_id='server')

    incoming = SyncManifest(
        node_id='tablet',
        checkpoint=0,
        node_time=0,
        payloads=[],
    )

    with pytest.raises(SyncAbortedError, match='checksum'):
        engine.process(incoming)


@patch('django_spire.contrib.sync.database.engine.time')
def test_process_clock_drift_aborts(
    mock_time: Any,
    storage: InMemoryDatabaseStorage,
) -> None:
    mock_time.time.return_value = 1000

    engine = _make_engine(storage, node_id='server', clock_drift_max=60)

    incoming = make_manifest(node_id='tablet', node_time=2000)

    with pytest.raises(SyncAbortedError, match='Clock drift'):
        engine.process(incoming)


@patch('django_spire.contrib.sync.database.engine.time')
def test_process_clock_drift_disabled(
    mock_time: Any,
    storage: InMemoryDatabaseStorage,
) -> None:
    mock_time.time.return_value = 1000

    engine = _make_engine(storage, node_id='server', clock_drift_max=None)

    incoming = make_manifest(node_id='tablet', node_time=9999)

    _response, result = engine.process(incoming)

    assert result.ok


@patch('django_spire.contrib.sync.database.engine.time')
def test_sync_pushes_local_changes(
    mock_time: Any,
    storage: InMemoryDatabaseStorage,
    empty_response: SyncManifest,
) -> None:
    mock_time.time.return_value = 500

    storage.seed(MODEL, '1', {'id': '1', 'name': 'Alice'}, {'name': 300})
    storage.save_checkpoint('tablet', 200)

    transport = FakeTransport(empty_response)
    engine = _make_engine(storage, transport=transport)

    engine.sync()

    assert transport.last_manifest is not None

    pushed_keys: set[str] = set()

    for payload in transport.last_manifest.payloads:
        if payload.model_label == MODEL:
            pushed_keys.update(payload.records.keys())

    assert '1' in pushed_keys


@patch('django_spire.contrib.sync.database.engine.time')
def test_sync_applies_remote_response(
    mock_time: Any,
    storage: InMemoryDatabaseStorage,
) -> None:
    mock_time.time.return_value = 500

    response = make_manifest(
        node_id='server',
        checkpoint=500,
        node_time=500,
        payloads=[
            ModelPayload(
                model_label=MODEL,
                records={
                    '99': make_record('99', {'id': '99', 'name': 'from-server'}, {'name': 400}),
                },
            ),
        ],
    )

    transport = FakeTransport(response)
    engine = _make_engine(storage, transport=transport)

    result = engine.sync()

    assert '99' in storage._records[MODEL]
    assert storage._records[MODEL]['99'].data['name'] == 'from-server'
    assert MODEL in result.applied


@patch('django_spire.contrib.sync.database.engine.time')
def test_sync_applies_conflict_resolved_response(
    mock_time: Any,
    storage: InMemoryDatabaseStorage,
) -> None:
    mock_time.time.return_value = 500

    storage.seed(
        MODEL, '1',
        {'id': '1', 'name': 'client-name', 'value': 10},
        {'name': 200, 'value': 100},
    )

    response = make_manifest(
        node_id='server',
        checkpoint=500,
        node_time=500,
        payloads=[
            ModelPayload(
                model_label=MODEL,
                records={
                    '1': make_record(
                        '1',
                        {'id': '1', 'name': 'client-name', 'value': 99},
                        {'name': 200, 'value': 150},
                    ),
                },
            ),
        ],
    )

    transport = FakeTransport(response)
    engine = _make_engine(storage, transport=transport)

    result = engine.sync()

    assert storage._records[MODEL]['1'].data['value'] == 99
    assert '1' in result.applied.get(MODEL, [])
    assert '1' not in result.skipped.get(MODEL, [])


@patch('django_spire.contrib.sync.database.engine.time')
def test_sync_skips_stale_response_record(
    mock_time: Any,
    storage: InMemoryDatabaseStorage,
) -> None:
    mock_time.time.return_value = 500

    storage.seed(
        MODEL, '1',
        {'id': '1', 'name': 'current'},
        {'name': 300},
    )

    response = make_manifest(
        node_id='server',
        checkpoint=500,
        node_time=500,
        payloads=[
            ModelPayload(
                model_label=MODEL,
                records={
                    '1': make_record(
                        '1',
                        {'id': '1', 'name': 'stale'},
                        {'name': 100},
                    ),
                },
            ),
        ],
    )

    transport = FakeTransport(response)
    engine = _make_engine(storage, transport=transport)

    result = engine.sync()

    assert storage._records[MODEL]['1'].data['name'] == 'current'
    assert '1' in result.skipped.get(MODEL, [])


@patch('django_spire.contrib.sync.database.engine.time')
def test_sync_tracks_response_deletes(
    mock_time: Any,
    storage: InMemoryDatabaseStorage,
) -> None:
    mock_time.time.return_value = 500

    storage.seed(MODEL, '1', {'id': '1', 'name': 'doomed'}, {'name': 100})

    response = make_manifest(
        node_id='server',
        checkpoint=500,
        node_time=500,
        payloads=[
            ModelPayload(model_label=MODEL, deletes={'1': 400}),
        ],
    )

    transport = FakeTransport(response)
    engine = _make_engine(storage, transport=transport)

    result = engine.sync()

    assert '1' not in storage._records[MODEL]
    assert '1' in result.deleted.get(MODEL, [])


@patch('django_spire.contrib.sync.database.engine.time')
def test_sync_response_delete_skipped_when_local_modified(
    mock_time: Any,
    storage: InMemoryDatabaseStorage,
) -> None:
    mock_time.time.return_value = 500

    storage.seed(
        MODEL, '1',
        {'id': '1', 'name': 'still-here'},
        {'name': 500},
    )

    response = make_manifest(
        node_id='server',
        checkpoint=500,
        node_time=500,
        payloads=[
            ModelPayload(model_label=MODEL, deletes={'1': 300}),
        ],
    )

    transport = FakeTransport(response)
    engine = _make_engine(storage, transport=transport)

    result = engine.sync()

    assert '1' in storage._records[MODEL]
    assert '1' in result.skipped.get(MODEL, [])
    assert '1' not in result.deleted.get(MODEL, [])


@patch('django_spire.contrib.sync.database.engine.time')
def test_sync_dry_run_does_not_mutate(
    mock_time: Any,
    storage: InMemoryDatabaseStorage,
) -> None:
    mock_time.time.return_value = 500

    response = make_manifest(
        node_id='server',
        checkpoint=500,
        node_time=500,
        payloads=[
            ModelPayload(
                model_label=MODEL,
                records={
                    '99': make_record('99', {'id': '99', 'name': 'from-server'}, {'name': 400}),
                },
            ),
        ],
    )

    transport = FakeTransport(response)
    engine = _make_engine(storage, transport=transport)

    engine.sync(dry_run=True)

    assert '99' not in storage._records[MODEL]


def test_sync_no_transport_raises(
    storage: InMemoryDatabaseStorage,
) -> None:
    engine = _make_engine(storage, transport=None)

    with pytest.raises(TransportRequiredError, match='Transport is required'):
        engine.sync()


@patch('django_spire.contrib.sync.database.engine.time')
def test_sync_saves_checkpoint(
    mock_time: Any,
    storage: InMemoryDatabaseStorage,
    empty_response: SyncManifest,
) -> None:
    mock_time.time.return_value = 500

    transport = FakeTransport(empty_response)
    engine = _make_engine(storage, transport=transport)

    engine.sync()

    assert storage.get_checkpoint('tablet') == empty_response.checkpoint


@patch('django_spire.contrib.sync.database.engine.time')
def test_sync_dry_run_does_not_save_checkpoint(
    mock_time: Any,
    storage: InMemoryDatabaseStorage,
    empty_response: SyncManifest,
) -> None:
    mock_time.time.return_value = 500

    transport = FakeTransport(empty_response)
    engine = _make_engine(storage, transport=transport)

    engine.sync(dry_run=True)

    assert storage.get_checkpoint('tablet') == 0


@patch('django_spire.contrib.sync.database.engine.time')
def test_sync_on_complete_callback(
    mock_time: Any,
    storage: InMemoryDatabaseStorage,
    empty_response: SyncManifest,
) -> None:
    mock_time.time.return_value = 500

    captured: list[Any] = []

    transport = FakeTransport(empty_response)
    engine = _make_engine(
        storage,
        transport=transport,
        on_complete=captured.append,
    )

    engine.sync()

    assert len(captured) == 1


@patch('django_spire.contrib.sync.database.engine.time')
def test_sync_response_clock_drift_aborts(
    mock_time: Any,
    storage: InMemoryDatabaseStorage,
) -> None:
    mock_time.time.return_value = 1000

    response = make_manifest(node_id='server', node_time=9999)
    transport = FakeTransport(response)

    engine = _make_engine(storage, transport=transport, clock_drift_max=60)

    with pytest.raises(SyncAbortedError, match='Clock drift'):
        engine.sync()


@patch('django_spire.contrib.sync.database.engine.time')
def test_sync_response_clock_drift_does_not_save_checkpoint(
    mock_time: Any,
    storage: InMemoryDatabaseStorage,
) -> None:
    mock_time.time.return_value = 1000

    response = make_manifest(
        node_id='server',
        checkpoint=9999,
        node_time=9999,
    )
    transport = FakeTransport(response)

    engine = _make_engine(storage, transport=transport, clock_drift_max=60)

    with pytest.raises(SyncAbortedError):
        engine.sync()

    assert storage.get_checkpoint('tablet') == 0


@patch('django_spire.contrib.sync.database.engine.time')
def test_sync_safe_checkpoint_preserves_new_unsent_changes(
    mock_time: Any,
    storage: InMemoryDatabaseStorage,
) -> None:
    mock_time.time.return_value = 500

    storage.save_checkpoint('tablet', 100)
    storage.seed(MODEL, '1', {'id': '1', 'name': 'sent'}, {'name': 200})

    def inject_new_record(s: InMemoryDatabaseStorage) -> None:
        s.seed(
            MODEL, '2',
            {'id': '2', 'name': 'unsent'},
            {'name': 150},
        )

    response = make_manifest(
        node_id='server',
        checkpoint=1000,
        node_time=500,
        payloads=[],
    )

    transport = _MutatingTransport(response, storage, inject_new_record)
    engine = _make_engine(storage, transport=transport)

    engine.sync()

    checkpoint = storage.get_checkpoint('tablet')

    assert checkpoint < 1000
    assert checkpoint <= 149


@patch('django_spire.contrib.sync.database.engine.time')
def test_sync_safe_checkpoint_preserves_modification_to_sent_record(
    mock_time: Any,
    storage: InMemoryDatabaseStorage,
) -> None:
    mock_time.time.return_value = 500

    storage.save_checkpoint('tablet', 100)
    storage.seed(MODEL, '1', {'id': '1', 'name': 'first-version'}, {'name': 200})

    def mutate_sent_record(s: InMemoryDatabaseStorage) -> None:
        s.seed(
            MODEL, '1',
            {'id': '1', 'name': 'second-version'},
            {'name': 250},
        )

    response = make_manifest(
        node_id='server',
        checkpoint=1000,
        node_time=500,
        payloads=[],
    )

    transport = _MutatingTransport(response, storage, mutate_sent_record)
    engine = _make_engine(storage, transport=transport)

    engine.sync()

    checkpoint = storage.get_checkpoint('tablet')

    assert checkpoint < 1000
    assert checkpoint <= 249


@patch('django_spire.contrib.sync.database.engine.time')
def test_sync_advances_clock_past_response_checkpoint(
    mock_time: Any,
    storage: InMemoryDatabaseStorage,
) -> None:
    mock_time.time.return_value = 500

    clock = HybridLogicalClock()
    clock._physical = lambda: 1_000

    high_checkpoint = 5_000 << 16

    response = make_manifest(
        node_id='server',
        checkpoint=high_checkpoint,
        node_time=500,
        payloads=[],
    )

    transport = FakeTransport(response)
    engine = _make_engine(storage, transport=transport, clock=clock)

    engine.sync()

    next_ts = clock.now()

    assert next_ts > high_checkpoint


@patch('django_spire.contrib.sync.database.engine.time')
def test_sync_local_write_after_response_is_not_stranded(
    mock_time: Any,
    storage: InMemoryDatabaseStorage,
) -> None:
    mock_time.time.return_value = 500

    clock = HybridLogicalClock()
    clock._physical = lambda: 1_000

    high_checkpoint = 5_000 << 16

    response = make_manifest(
        node_id='server',
        checkpoint=high_checkpoint,
        node_time=500,
        payloads=[],
    )

    transport = FakeTransport(response)
    engine = _make_engine(storage, transport=transport, clock=clock)

    engine.sync()

    local_ts = clock.now()
    storage.seed(
        MODEL, 'after',
        {'id': 'after', 'name': 'written-after-sync'},
        {'name': local_ts},
    )

    saved_checkpoint = storage.get_checkpoint('tablet')

    assert local_ts > saved_checkpoint

    changes = storage.get_changed_since(MODEL, saved_checkpoint)

    assert 'after' in changes


def test_apply_response_orders_by_sync_dependency(
    storage: InMemoryDatabaseStorage,
) -> None:
    _ = storage

    parent_label = 'app.Parent'
    child_label = 'app.Child'

    multi_storage = InMemoryDatabaseStorage([parent_label, child_label])
    graph = DependencyGraph({
        parent_label: set(),
        child_label: {parent_label},
    })

    engine = DatabaseEngine(
        storage=multi_storage,
        graph=graph,
        clock=HybridLogicalClock(),
        node_id='tablet',
        clock_drift_max=None,
    )

    response = SyncManifest(
        node_id='server',
        checkpoint=0,
        node_time=0,
        payloads=[
            ModelPayload(
                model_label=child_label,
                records={
                    '1': make_record('1', {'id': '1'}, {'id': 100}),
                },
            ),
            ModelPayload(
                model_label=parent_label,
                records={
                    'p': make_record('p', {'id': 'p'}, {'id': 100}),
                },
            ),
        ],
    )

    ordered = engine._order_payloads(response.payloads)

    assert ordered[0].model_label == parent_label
    assert ordered[1].model_label == child_label


def test_detect_field_conflicts() -> None:
    reconciler = PayloadReconciler()

    local = make_record('1', {'name': 'A', 'value': 10}, {'name': 200, 'value': 50})
    remote = make_record('1', {'name': 'B', 'value': 10}, {'name': 300, 'value': 50})

    conflicts = reconciler._detect_field_conflicts(local, remote, 100)

    assert len(conflicts) == 1
    assert conflicts[0].field_name == 'name'
    assert conflicts[0].local_value == 'A'
    assert conflicts[0].remote_value == 'B'


def test_detect_field_conflicts_same_value_no_conflict() -> None:
    reconciler = PayloadReconciler()

    local = make_record('1', {'name': 'same'}, {'name': 200})
    remote = make_record('1', {'name': 'same'}, {'name': 300})

    conflicts = reconciler._detect_field_conflicts(local, remote, 100)

    assert len(conflicts) == 0


def test_detect_field_conflicts_before_checkpoint_ignored() -> None:
    reconciler = PayloadReconciler()

    local = make_record('1', {'name': 'A'}, {'name': 50})
    remote = make_record('1', {'name': 'B'}, {'name': 300})

    conflicts = reconciler._detect_field_conflicts(local, remote, 100)

    assert len(conflicts) == 0


def test_upsert_skips_ghost_record(
    storage: InMemoryDatabaseStorage,
) -> None:
    records = {
        'ghost': SyncRecord(
            key='ghost',
            data={'id': 'ghost', 'name': 'Ghost'},
            timestamps={},
        ),
    }

    skipped = storage.upsert_many(MODEL, records)

    assert 'ghost' in skipped
    assert 'ghost' not in storage._records[MODEL]
