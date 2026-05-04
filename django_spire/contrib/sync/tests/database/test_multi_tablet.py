from __future__ import annotations

import random

import pytest

from hypothesis import given, settings
from hypothesis import strategies as st

from django_spire.contrib.sync.tests.database.harness import ModelSchema, MultiTabletHarness
from django_spire.contrib.sync.tests.database.schemas import (
    FLAT_SCHEMA,
    HIERARCHICAL_SCHEMA,
    WIDE_SCHEMA,
)


class TestMultiTabletBasics:
    def test_single_tablet_create_and_sync(self) -> None:
        harness = MultiTabletHarness(tablet_count=1, schemas=FLAT_SCHEMA, seed=42)
        ts = harness.ts()

        harness.tablet_save(
            'tablet_1', 'app.Record', 'r-1',
            {'id': 'r-1', 'name': 'alpha', 'value': 10, 'is_active': True},
            {'name': ts, 'value': ts, 'is_active': ts},
        )

        harness.sync_all()
        harness.assert_converged('app.Record')

    def test_two_tablets_disjoint_records(self) -> None:
        harness = MultiTabletHarness(tablet_count=2, schemas=FLAT_SCHEMA, seed=42)
        ts = harness.ts()

        harness.tablet_save(
            'tablet_1', 'app.Record', 'r-1',
            {'id': 'r-1', 'name': 'from-tablet-1', 'value': 1},
            {'name': ts, 'value': ts},
        )

        harness.tablet_save(
            'tablet_2', 'app.Record', 'r-2',
            {'id': 'r-2', 'name': 'from-tablet-2', 'value': 2},
            {'name': ts, 'value': ts},
        )

        harness.sync_all_converge()
        harness.assert_converged('app.Record')

        assert harness.tablet_record('tablet_1', 'app.Record', 'r-2') is not None
        assert harness.tablet_record('tablet_2', 'app.Record', 'r-1') is not None

    def test_three_tablets_all_converge(self) -> None:
        harness = MultiTabletHarness(tablet_count=3, schemas=FLAT_SCHEMA, seed=42)

        for i, tablet_id in enumerate(harness.tablet_ids):
            ts = harness.ts()
            harness.tablet_save(
                tablet_id, 'app.Record', f'r-{i}',
                {'id': f'r-{i}', 'name': f'from-{tablet_id}', 'value': i},
                {'name': ts, 'value': ts},
            )

        harness.sync_all_converge()
        harness.assert_converged('app.Record')

        for i in range(3):
            for tablet_id in harness.tablet_ids:
                assert harness.tablet_record(tablet_id, 'app.Record', f'r-{i}') is not None

    def test_five_tablets_converge(self) -> None:
        harness = MultiTabletHarness(tablet_count=5, schemas=FLAT_SCHEMA, seed=99)

        for tablet_id in harness.tablet_ids:
            keys = harness.seed_records('app.Record', 3, target=tablet_id)
            assert len(keys) == 3

        harness.sync_all_converge(rounds=3)
        harness.assert_converged('app.Record')


class TestMultiTabletConflicts:
    def test_two_tablets_same_key_different_fields(self) -> None:
        harness = MultiTabletHarness(tablet_count=2, schemas=FLAT_SCHEMA, seed=42)

        early = harness.ts()
        ts1 = harness.ts()
        ts2 = harness.ts()

        harness.tablet_save(
            'tablet_1', 'app.Record', 'r-1',
            {'id': 'r-1', 'name': 'tablet-1-name', 'value': 100, 'is_active': True},
            {'name': ts1, 'value': early, 'is_active': early},
        )

        harness.tablet_save(
            'tablet_2', 'app.Record', 'r-1',
            {'id': 'r-1', 'name': 'tablet-2-name', 'value': 200, 'is_active': False},
            {'name': early, 'value': ts2, 'is_active': early},
        )

        harness.sync_all_converge()
        harness.assert_converged('app.Record')

        server = harness.server_record('app.Record', 'r-1')
        assert server.data['name'] == 'tablet-1-name'
        assert server.data['value'] == 200

    def test_same_field_higher_timestamp_wins(self) -> None:
        harness = MultiTabletHarness(tablet_count=2, schemas=FLAT_SCHEMA, seed=42)

        ts_low = harness.ts()
        ts_high = harness.ts()

        harness.tablet_save(
            'tablet_1', 'app.Record', 'r-1',
            {'id': 'r-1', 'name': 'loser'},
            {'name': ts_low},
        )

        harness.tablet_save(
            'tablet_2', 'app.Record', 'r-1',
            {'id': 'r-1', 'name': 'winner'},
            {'name': ts_high},
        )

        harness.sync_all_converge()
        harness.assert_converged('app.Record')

        assert harness.server_record('app.Record', 'r-1').data['name'] == 'winner'


class TestDependencyOrdering:
    def test_parent_child_sync(self) -> None:
        harness = MultiTabletHarness(
            tablet_count=2, schemas=HIERARCHICAL_SCHEMA, seed=42,
        )
        ts = harness.ts()

        harness.tablet_save(
            'tablet_1', 'app.Parent', 'p-1',
            {'id': 'p-1', 'name': 'parent', 'value': 10},
            {'name': ts, 'value': ts},
        )

        harness.tablet_save(
            'tablet_1', 'app.Child', 'c-1',
            {'id': 'c-1', 'parent_id': 'p-1', 'x': 1.0, 'y': 2.0, 'is_active': True},
            {'parent_id': ts, 'x': ts, 'y': ts, 'is_active': ts},
        )

        harness.sync_all_converge()

        assert harness.server_record('app.Parent', 'p-1') is not None
        assert harness.server_record('app.Child', 'c-1') is not None
        assert harness.tablet_record('tablet_2', 'app.Parent', 'p-1') is not None
        assert harness.tablet_record('tablet_2', 'app.Child', 'c-1') is not None


class TestIdempotency:
    def test_repeated_sync_stable(self) -> None:
        harness = MultiTabletHarness(tablet_count=3, schemas=FLAT_SCHEMA, seed=42)

        for tablet_id in harness.tablet_ids:
            ts = harness.ts()
            harness.tablet_save(
                tablet_id, 'app.Record', 'shared',
                {'id': 'shared', 'name': f'from-{tablet_id}'},
                {'name': ts},
            )

        harness.sync_all_converge()

        snapshot = dict(harness.server_record('app.Record', 'shared').data)

        for _ in range(5):
            harness.sync_all()

        assert harness.server_record('app.Record', 'shared').data == snapshot

    def test_empty_sync_no_errors(self) -> None:
        harness = MultiTabletHarness(tablet_count=3, schemas=FLAT_SCHEMA, seed=42)

        for _ in range(10):
            harness.sync_all()


class TestScaleParameters:
    @pytest.mark.parametrize('tablet_count', [1, 2, 3, 5])
    def test_variable_tablet_count(self, tablet_count: int) -> None:
        harness = MultiTabletHarness(
            tablet_count=tablet_count, schemas=FLAT_SCHEMA, seed=42,
        )

        harness.seed_records('app.Record', 10, target='server')
        harness.sync_all_converge()
        harness.assert_converged('app.Record')

        for tablet_id in harness.tablet_ids:
            records = harness.all_tablet_records('app.Record')[tablet_id]
            assert len(records) == 10

    @pytest.mark.parametrize('record_count', [1, 10, 50, 100])
    def test_variable_record_count(self, record_count: int) -> None:
        harness = MultiTabletHarness(
            tablet_count=2, schemas=FLAT_SCHEMA, seed=42,
        )

        harness.seed_records('app.Record', record_count, target='tablet_1')
        harness.sync_all_converge()
        harness.assert_converged('app.Record')

        assert len(harness.server_records('app.Record')) == record_count

    def test_wide_schema_20_fields(self) -> None:
        harness = MultiTabletHarness(
            tablet_count=2, schemas=WIDE_SCHEMA, seed=42,
        )

        harness.seed_records('app.Wide', 10, target='tablet_1')
        harness.sync_all_converge()
        harness.assert_converged('app.Wide')

        record = harness.server_record('app.Wide', 'wide-0')
        assert len([k for k in record.data if k != 'id']) == 20


class TestConcurrentOperations:
    def test_interleaved_writes_and_syncs(self) -> None:
        harness = MultiTabletHarness(
            tablet_count=3, schemas=FLAT_SCHEMA, seed=42,
        )

        harness.run_random_operations(
            'app.Record',
            num_operations=50,
            num_keys=5,
            sync_probability=0.3,
        )

        harness.sync_all_converge(rounds=3)
        harness.assert_converged('app.Record')

    def test_high_contention_single_key(self) -> None:
        harness = MultiTabletHarness(
            tablet_count=3, schemas=FLAT_SCHEMA, seed=42,
        )

        harness.run_random_operations(
            'app.Record',
            num_operations=30,
            num_keys=1,
            sync_probability=0.25,
        )

        harness.sync_all_converge(rounds=3)
        harness.assert_converged('app.Record')

    def test_staggered_sync_order(self) -> None:
        harness = MultiTabletHarness(
            tablet_count=3, schemas=FLAT_SCHEMA, seed=42,
        )

        for tablet_id in harness.tablet_ids:
            ts = harness.ts()
            harness.tablet_save(
                tablet_id, 'app.Record', 'shared',
                {'id': 'shared', 'name': f'from-{tablet_id}', 'value': 1},
                {'name': ts, 'value': ts},
            )

        harness.sync_tablet('tablet_3')
        harness.sync_tablet('tablet_1')
        harness.sync_tablet('tablet_2')

        harness.sync_all_converge()
        harness.assert_converged('app.Record')


class TestRandomizedConvergence:
    @given(
        seed=st.integers(min_value=0, max_value=2**32),
        tablet_count=st.integers(min_value=2, max_value=5),
        num_operations=st.integers(min_value=10, max_value=50),
    )
    @settings(max_examples=30, deadline=10_000)
    def test_random_operations_always_converge(
        self,
        seed: int,
        tablet_count: int,
        num_operations: int,
    ) -> None:
        harness = MultiTabletHarness(
            tablet_count=tablet_count,
            schemas=FLAT_SCHEMA,
            seed=seed,
        )

        harness.run_random_operations(
            'app.Record',
            num_operations=num_operations,
            num_keys=5,
            sync_probability=0.2,
        )

        harness.sync_all_converge(rounds=3)
        harness.assert_converged('app.Record')

    @given(
        seed=st.integers(min_value=0, max_value=2**32),
        num_fields=st.integers(min_value=1, max_value=15),
        num_records=st.integers(min_value=1, max_value=20),
    )
    @settings(max_examples=30, deadline=10_000)
    def test_variable_schema_width_converges(
        self,
        seed: int,
        num_fields: int,
        num_records: int,
    ) -> None:
        schemas = [
            ModelSchema(
                label='app.Dynamic',
                fields=[f'f_{i}' for i in range(num_fields)],
            ),
        ]

        harness = MultiTabletHarness(
            tablet_count=3,
            schemas=schemas,
            seed=seed,
        )

        harness.seed_records('app.Dynamic', num_records, target='tablet_1')

        rng = random.Random(seed)

        for _ in range(15):
            tablet_id = rng.choice(harness.tablet_ids)
            key = f'dynamic-{rng.randint(0, num_records - 1)}'
            ts = harness.ts()
            field_name = f'f_{rng.randint(0, num_fields - 1)}'

            existing = harness.tablet_record(tablet_id, 'app.Dynamic', key)

            if existing is not None:
                data = dict(existing.data)
                timestamps = dict(existing.timestamps)
            else:
                data = {'id': key}
                timestamps = {}

            data[field_name] = rng.randint(0, 999)
            timestamps[field_name] = ts

            harness.tablet_save(tablet_id, 'app.Dynamic', key, data, timestamps)

        harness.sync_all_converge(rounds=3)
        harness.assert_converged('app.Dynamic')

    @given(
        seed=st.integers(min_value=0, max_value=2**32),
        tablet_count=st.integers(min_value=2, max_value=5),
    )
    @settings(max_examples=20, deadline=10_000)
    def test_hierarchical_random_convergence(
        self,
        seed: int,
        tablet_count: int,
    ) -> None:
        harness = MultiTabletHarness(
            tablet_count=tablet_count,
            schemas=HIERARCHICAL_SCHEMA,
            seed=seed,
        )

        rng = random.Random(seed)
        parent_keys = [f'p-{i}' for i in range(3)]

        for key in parent_keys:
            ts = harness.ts()
            tablet_id = rng.choice(harness.tablet_ids)
            harness.tablet_save(
                tablet_id, 'app.Parent', key,
                {'id': key, 'name': f'parent-{key}', 'value': rng.randint(0, 100)},
                {'name': ts, 'value': ts},
            )

        for i in range(10):
            ts = harness.ts()
            tablet_id = rng.choice(harness.tablet_ids)
            parent_key = rng.choice(parent_keys)
            child_key = f'c-{i}'

            harness.tablet_save(
                tablet_id, 'app.Child', child_key,
                {
                    'id': child_key,
                    'parent_id': parent_key,
                    'x': rng.uniform(-90, 90),
                    'y': rng.uniform(-180, 180),
                    'is_active': rng.choice([True, False]),
                },
                {'parent_id': ts, 'x': ts, 'y': ts, 'is_active': ts},
            )

            if rng.random() < 0.3:
                harness.sync_tablet(rng.choice(harness.tablet_ids))

        harness.sync_all_converge(rounds=3)
        harness.assert_converged('app.Parent')
        harness.assert_converged('app.Child')
