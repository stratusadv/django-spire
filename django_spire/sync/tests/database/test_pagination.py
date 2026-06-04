from __future__ import annotations

import random

from contextlib import nullcontext
from typing import Any
from unittest.mock import patch

import pytest

from hypothesis import given, settings
from hypothesis import strategies as st

from django_spire.sync.core.clock import HybridLogicalClock
from django_spire.sync.database.conflict import FieldTimestampWins
from django_spire.sync.database.engine import DatabaseEngine, _record_size
from django_spire.sync.database.graph import DependencyGraph
from django_spire.sync.database.manifest import SyncManifest
from django_spire.sync.database.reconciler import PayloadReconciler
from django_spire.sync.database.record import SyncRecord
from django_spire.sync.tests.database.helpers import (
    DirectTransport,
    InMemoryDatabaseStorage,
    MODEL,
    STAKE,
    SURVEY,
)


def _make_storage(models: list[str] | None = None) -> InMemoryDatabaseStorage:
    return InMemoryDatabaseStorage(models or [MODEL])


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

    peer_node_id = 'server' if transport is not None else None

    return DatabaseEngine(
        batch_bytes=batch_bytes,
        batch_size=batch_size,
        clock=clock,
        clock_drift_max=None,
        graph=graph,
        node_id=node_id,
        peer_node_id=peer_node_id,
        reconciler=PayloadReconciler(resolver=FieldTimestampWins()),
        storage=storage,
        transaction=nullcontext,
        transport=transport,
    )


def _make_engine_graph(
    storage: InMemoryDatabaseStorage,
    node_id: str,
    clock: HybridLogicalClock,
    edges: dict[str, set[str]],
    transport: Any = None,
    batch_size: int | None = None,
    batch_bytes: int | None = None,
) -> DatabaseEngine:
    graph = DependencyGraph(edges)
    peer_node_id = 'server' if transport is not None else None

    return DatabaseEngine(
        batch_bytes=batch_bytes,
        batch_size=batch_size,
        clock=clock,
        clock_drift_max=None,
        graph=graph,
        node_id=node_id,
        peer_node_id=peer_node_id,
        reconciler=PayloadReconciler(resolver=FieldTimestampWins()),
        storage=storage,
        transaction=nullcontext,
        transport=transport,
    )


def _seed_records(
    storage: InMemoryDatabaseStorage, count: int, base_ts: int = 1000, prefix: str = ''
) -> dict[str, SyncRecord]:
    records: dict[str, SyncRecord] = {}

    for i in range(count):
        key = f'{prefix}key-{i:04d}'
        ts = base_ts + i

        storage.seed(MODEL, key, {'id': key, 'value': i}, {'id': ts, 'value': ts})

        records[key] = storage._records[MODEL][key]

    return records


@pytest.fixture(autouse=True)
def _fixed_time() -> Any:
    with patch('django_spire.sync.database.engine.time') as mock_time:
        mock_time.time.return_value = 1000
        yield mock_time


class _CappedDirectTransport(DirectTransport):
    def __init__(self, server_engine: DatabaseEngine, exchange_count_max: int = 100) -> None:
        super().__init__(server_engine)
        self._exchange_count_max = exchange_count_max

    def exchange(self, manifest: SyncManifest) -> SyncManifest:
        if len(self.exchanges) >= self._exchange_count_max:
            message = f'Sync exceeded {self._exchange_count_max} exchanges without converging'

            raise AssertionError(message)

        return super().exchange(manifest)


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
            key: dict(record.timestamps) for key, record in tablet_storage._records[MODEL].items()
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

        peer_seq = tablet_storage.get_checkpoint('server').peer_sequence
        max_seeded_seq = max(r.sequence for r in seeded.values())

        assert peer_seq >= max_seeded_seq

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

        server_storage.seed(
            MODEL, 'new-key', {'id': 'new-key', 'value': 999}, {'id': new_ts, 'value': new_ts}
        )

        tablet.sync()

        assert 'new-key' in tablet_storage._records[MODEL]
        assert len(tablet_storage._records[MODEL]) == 51


class TestBatchSizeVariations:
    @pytest.mark.parametrize('batch_size', [1, 3, 7, 13, 50, 100, 200])
    def test_all_records_arrive_regardless_of_batch_size(self, batch_size: int) -> None:
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
    def test_resync_is_noop_regardless_of_batch_size(self, batch_size: int) -> None:
        clock = HybridLogicalClock()

        server_storage = _make_storage()
        _seed_records(server_storage, count=100)
        server = _make_engine(server_storage, 'server', clock, batch_size=batch_size)

        tablet_storage = _make_storage()
        transport = DirectTransport(server)
        tablet = _make_engine(tablet_storage, 'tablet', clock, transport, batch_size=batch_size)

        tablet.sync()

        result = tablet.sync()

        total = sum(len(k) for k in result.applied.values()) + sum(
            len(k) for k in result.created.values()
        )

        assert total == 0


class TestInterleavedSequenceConvergence:
    def test_late_model_with_low_sequence_converges(self) -> None:
        clock = HybridLogicalClock()
        edges = {SURVEY: set(), STAKE: {SURVEY}}

        server_storage = _make_storage([SURVEY, STAKE])
        server_storage.seed(
            STAKE,
            'stake-low',
            {'id': 'stake-low', 'survey_id': 'survey-00', 'value': 1},
            {'survey_id': 1000, 'value': 1000},
        )

        for i in range(50):
            server_storage.seed(
                SURVEY,
                f'survey-{i:02d}',
                {'id': f'survey-{i:02d}', 'value': i},
                {'value': 1000 + i + 1},
            )

        server = _make_engine_graph(server_storage, 'server', clock, edges, batch_size=10)

        tablet_storage = _make_storage([SURVEY, STAKE])
        transport = _CappedDirectTransport(server, exchange_count_max=100)
        tablet = _make_engine_graph(
            tablet_storage, 'tablet', clock, edges, transport, batch_size=10
        )

        tablet.sync()

        assert len(tablet_storage._records[SURVEY]) == 50
        assert len(tablet_storage._records[STAKE]) == 1

    def test_tombstone_on_skipped_model_is_delivered(self) -> None:
        clock = HybridLogicalClock()
        edges = {SURVEY: set(), STAKE: {SURVEY}}

        server_storage = _make_storage([SURVEY, STAKE])
        server_storage.seed(
            STAKE,
            'stake-doomed',
            {'id': 'stake-doomed', 'survey_id': 'survey-00', 'value': 1},
            {'survey_id': 1000, 'value': 1000},
        )

        server = _make_engine_graph(server_storage, 'server', clock, edges, batch_size=10)

        tablet_storage = _make_storage([SURVEY, STAKE])
        transport = _CappedDirectTransport(server, exchange_count_max=100)
        tablet = _make_engine_graph(
            tablet_storage, 'tablet', clock, edges, transport, batch_size=10
        )

        tablet.sync()

        assert 'stake-doomed' in tablet_storage._records[STAKE]

        delete_ts = clock.now()
        server_storage.delete_many(STAKE, {'stake-doomed': delete_ts}, '')

        for i in range(50):
            server_storage.seed(
                SURVEY,
                f'survey-{i:02d}',
                {'id': f'survey-{i:02d}', 'value': i},
                {'value': clock.now()},
            )

        server_storage.seed(
            STAKE,
            'stake-new',
            {'id': 'stake-new', 'survey_id': 'survey-00', 'value': 2},
            {'survey_id': clock.now(), 'value': clock.now()},
        )

        tablet.sync()

        assert 'stake-doomed' not in tablet_storage._records[STAKE]
        assert 'stake-new' in tablet_storage._records[STAKE]
        assert len(tablet_storage._records[SURVEY]) == 50

    @given(
        seed=st.integers(min_value=0, max_value=2**32),
        record_count=st.integers(min_value=10, max_value=60),
        batch_size=st.sampled_from([1, 3, 7]),
    )
    @settings(max_examples=50, deadline=20_000)
    def test_random_interleaved_sequences_converge(
        self, seed: int, record_count: int, batch_size: int
    ) -> None:
        rng = random.Random(seed)
        clock = HybridLogicalClock()
        edges = {SURVEY: set(), STAKE: {SURVEY}}

        server_storage = _make_storage([SURVEY, STAKE])

        survey_count = 0
        stake_count = 0

        for i in range(record_count):
            if rng.random() < 0.5:
                key = f'survey-{survey_count}'
                survey_count += 1
                server_storage.seed(SURVEY, key, {'id': key, 'value': i}, {'value': clock.now()})
            else:
                key = f'stake-{stake_count}'
                stake_count += 1
                server_storage.seed(
                    STAKE,
                    key,
                    {'id': key, 'survey_id': 'survey-0', 'value': i},
                    {'value': clock.now()},
                )

        server = _make_engine_graph(server_storage, 'server', clock, edges, batch_size=batch_size)

        tablet_storage = _make_storage([SURVEY, STAKE])
        transport = _CappedDirectTransport(server, exchange_count_max=1000)
        tablet = _make_engine_graph(
            tablet_storage, 'tablet', clock, edges, transport, batch_size=batch_size
        )

        tablet.sync()

        assert len(tablet_storage._records[SURVEY]) == survey_count
        assert len(tablet_storage._records[STAKE]) == stake_count


class TestByteBudgetParentChildOrdering:
    def _seed_parent_then_child(
        self,
        storage: InMemoryDatabaseStorage,
        clock: HybridLogicalClock,
        survey_count: int,
        child_parent_key: str,
    ) -> None:
        for i in range(survey_count):
            storage.seed(
                SURVEY,
                f'survey-{i:02d}',
                {'id': f'survey-{i:02d}', 'value': i, 'blob': 'x' * 500},
                {'value': clock.now(), 'blob': clock.now()},
            )

        storage.seed(
            STAKE,
            'stake-0',
            {'id': 'stake-0', 'survey_id': child_parent_key, 'value': 1},
            {'survey_id': clock.now(), 'value': clock.now()},
        )

    def _byte_budget_for_one_parent_plus_child(self, storage: InMemoryDatabaseStorage) -> int:
        survey_size = _record_size(storage._records[SURVEY]['survey-00'])
        stake_size = _record_size(storage._records[STAKE]['stake-0'])
        return survey_size + stake_size + 1

    def test_server_response_excludes_child_when_parent_truncates(self) -> None:
        clock = HybridLogicalClock()
        edges = {SURVEY: set(), STAKE: {SURVEY}}

        server_storage = _make_storage([SURVEY, STAKE])
        self._seed_parent_then_child(
            server_storage, clock, survey_count=8, child_parent_key='survey-07'
        )

        server = _make_engine_graph(
            server_storage,
            'server',
            clock,
            edges,
            batch_bytes=self._byte_budget_for_one_parent_plus_child(server_storage),
        )

        incoming = SyncManifest(
            node_id='tablet', peer_sequence=0, local_sequence=0, node_time=1000, payloads=[]
        )
        incoming.checksum = incoming.compute_checksum()

        response, _result = server.process(incoming)
        labels = {payload.model_label for payload in response.payloads}

        assert SURVEY in labels
        assert STAKE not in labels, 'child shipped in a round where parent truncated mid-page'
        assert response.has_more

    def test_child_never_ships_before_parent_across_byte_paginated_pull(self) -> None:
        clock = HybridLogicalClock()
        edges = {SURVEY: set(), STAKE: {SURVEY}}

        server_storage = _make_storage([SURVEY, STAKE])
        self._seed_parent_then_child(
            server_storage, clock, survey_count=8, child_parent_key='survey-07'
        )

        server = _make_engine_graph(
            server_storage,
            'server',
            clock,
            edges,
            batch_bytes=self._byte_budget_for_one_parent_plus_child(server_storage),
        )

        tablet_storage = _make_storage([SURVEY, STAKE])
        transport = _CappedDirectTransport(server, exchange_count_max=500)
        tablet = _make_engine_graph(
            tablet_storage,
            'tablet',
            clock,
            edges,
            transport,
            batch_bytes=self._byte_budget_for_one_parent_plus_child(server_storage),
        )

        tablet.sync()

        delivered_surveys: set[str] = set()
        violations: list[tuple[str, Any]] = []

        for _wire_in, wire_out in transport.exchanges:
            for payload in wire_out.payloads:
                if payload.model_label == SURVEY:
                    delivered_surveys.update(payload.records.keys())

            for payload in wire_out.payloads:
                if payload.model_label != STAKE:
                    continue

                for key, record in payload.records.items():
                    parent_key = record.data.get('survey_id')

                    if parent_key not in delivered_surveys:
                        violations.append((key, parent_key))

        assert not violations, f'child(ren) shipped before their parent: {violations}'

        assert len(tablet_storage._records[SURVEY]) == 8
        assert len(tablet_storage._records[STAKE]) == 1

    def test_record_budget_truncation_still_orders_parent_before_child(self) -> None:
        clock = HybridLogicalClock()
        edges = {SURVEY: set(), STAKE: {SURVEY}}

        server_storage = _make_storage([SURVEY, STAKE])
        self._seed_parent_then_child(
            server_storage, clock, survey_count=8, child_parent_key='survey-07'
        )

        server = _make_engine_graph(server_storage, 'server', clock, edges, batch_size=3)

        tablet_storage = _make_storage([SURVEY, STAKE])
        transport = _CappedDirectTransport(server, exchange_count_max=500)
        tablet = _make_engine_graph(tablet_storage, 'tablet', clock, edges, transport, batch_size=3)

        tablet.sync()

        assert len(tablet_storage._records[SURVEY]) == 8
        assert len(tablet_storage._records[STAKE]) == 1
