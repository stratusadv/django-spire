from __future__ import annotations

import random

from typing import Any

from hypothesis import given, settings
from hypothesis import strategies as st

from django_spire.contrib.sync.tests.database.helpers import (
    SURVEY,
    STAKE,
    SyncHarness,
)


class TestTwoPartyConvergence:
    def test_tablet_create_then_sync(self) -> None:
        harness = SyncHarness()
        ts = harness.ts()

        harness.tablet_save(
            STAKE, 'st-1',
            {'id': 'st-1', 'latitude': 49.69, 'is_driven': True},
            {'latitude': ts, 'is_driven': ts},
        )

        harness.sync()
        harness.assert_converged(STAKE) if hasattr(harness, 'assert_converged') else None

        tablet = harness.tablet_record(STAKE, 'st-1')
        server = harness.server_record(STAKE, 'st-1')

        assert tablet is not None
        assert server is not None
        assert tablet.data == server.data

    def test_server_create_then_sync(self) -> None:
        harness = SyncHarness()
        ts = harness.ts()

        harness.server_save(
            STAKE, 'st-1',
            {'id': 'st-1', 'latitude': 50.0, 'is_reference': True},
            {'latitude': ts, 'is_reference': ts},
        )

        harness.sync()

        tablet = harness.tablet_record(STAKE, 'st-1')
        server = harness.server_record(STAKE, 'st-1')

        assert tablet is not None
        assert server is not None
        assert tablet.data == server.data

    def test_both_create_disjoint_keys(self) -> None:
        harness = SyncHarness()
        ts = harness.ts()

        harness.tablet_save(
            STAKE, 'st-tab',
            {'id': 'st-tab', 'latitude': 49.0},
            {'latitude': ts},
        )

        harness.server_save(
            STAKE, 'st-srv',
            {'id': 'st-srv', 'latitude': 50.0},
            {'latitude': ts},
        )

        harness.sync()

        tablet_keys = set(harness.tablet_storage._records[STAKE].keys())
        server_keys = set(harness.server_storage._records[STAKE].keys())

        assert tablet_keys == server_keys
        assert harness.tablet_record(STAKE, 'st-srv') is not None
        assert harness.server_record(STAKE, 'st-tab') is not None

        for key in tablet_keys:
            tablet = harness.tablet_record(STAKE, key)
            server = harness.server_record(STAKE, key)
            assert tablet.data == server.data

    def test_both_modify_same_key_different_fields(self) -> None:
        harness = SyncHarness()
        early = harness.ts()
        tablet_ts = harness.ts()
        server_ts = harness.ts()

        harness.tablet_save(
            STAKE, 'st-1',
            {'id': 'st-1', 'latitude': 49.69, 'is_driven': False},
            {'latitude': tablet_ts, 'is_driven': early},
        )

        harness.server_save(
            STAKE, 'st-1',
            {'id': 'st-1', 'latitude': 0.0, 'is_driven': True},
            {'latitude': early, 'is_driven': server_ts},
        )

        harness.sync()

        tablet = harness.tablet_record(STAKE, 'st-1')
        server = harness.server_record(STAKE, 'st-1')

        assert tablet.data == server.data
        assert tablet.data['latitude'] == 49.69
        assert tablet.data['is_driven'] is True

    def test_both_modify_same_field_higher_timestamp_wins(self) -> None:
        harness = SyncHarness()
        ts_low = harness.ts()
        ts_high = harness.ts()

        harness.tablet_save(
            STAKE, 'st-1',
            {'id': 'st-1', 'latitude': 49.0},
            {'latitude': ts_low},
        )

        harness.server_save(
            STAKE, 'st-1',
            {'id': 'st-1', 'latitude': 50.0},
            {'latitude': ts_high},
        )

        harness.sync()

        tablet = harness.tablet_record(STAKE, 'st-1')
        server = harness.server_record(STAKE, 'st-1')

        assert tablet.data == server.data
        assert tablet.data['latitude'] == 50.0

    def test_parent_child_ordering(self) -> None:
        harness = SyncHarness()
        ts = harness.ts()

        harness.tablet_save(
            SURVEY, 'sv-1',
            {'id': 'sv-1', 'stake_spacing': 40},
            {'stake_spacing': ts},
        )

        harness.tablet_save(
            STAKE, 'st-1',
            {'id': 'st-1', 'survey_id': 'sv-1', 'latitude': 49.0},
            {'survey_id': ts, 'latitude': ts},
        )

        harness.sync()

        for model, key in [(SURVEY, 'sv-1'), (STAKE, 'st-1')]:
            tablet = harness.tablet_record(model, key)
            server = harness.server_record(model, key)

            assert tablet is not None
            assert server is not None
            assert tablet.data == server.data


class TestIdempotency:
    def test_repeated_sync_no_changes(self) -> None:
        harness = SyncHarness()
        ts = harness.ts()

        harness.tablet_save(
            STAKE, 'st-1',
            {'id': 'st-1', 'latitude': 49.0},
            {'latitude': ts},
        )

        harness.sync()

        snapshot_tablet = dict(harness.tablet_record(STAKE, 'st-1').data)
        snapshot_server = dict(harness.server_record(STAKE, 'st-1').data)

        for _ in range(5):
            harness.sync()

        assert harness.tablet_record(STAKE, 'st-1').data == snapshot_tablet
        assert harness.server_record(STAKE, 'st-1').data == snapshot_server

    def test_empty_sync_is_safe(self) -> None:
        harness = SyncHarness()

        for _ in range(10):
            result = harness.tablet_engine.sync()
            assert result.ok

    def test_timestamps_stable_across_idempotent_syncs(self) -> None:
        harness = SyncHarness()
        ts = harness.ts()

        harness.tablet_save(
            STAKE, 'st-1',
            {'id': 'st-1', 'latitude': 49.0},
            {'latitude': ts},
        )

        harness.sync()

        ts_before = dict(harness.server_record(STAKE, 'st-1').timestamps)

        harness.sync()
        harness.sync()

        ts_after = dict(harness.server_record(STAKE, 'st-1').timestamps)

        assert ts_before == ts_after


class TestMultiCycleConvergence:
    def test_update_after_initial_sync(self) -> None:
        harness = SyncHarness()
        ts1 = harness.ts()

        harness.tablet_save(
            STAKE, 'st-1',
            {'id': 'st-1', 'latitude': 49.0, 'is_driven': False},
            {'latitude': ts1, 'is_driven': ts1},
        )

        harness.sync()

        assert harness.server_record(STAKE, 'st-1').data['latitude'] == 49.0

        ts2 = harness.ts()

        harness.tablet_save(
            STAKE, 'st-1',
            {'id': 'st-1', 'latitude': 49.5, 'is_driven': True},
            {'latitude': ts2, 'is_driven': ts2},
        )

        harness.sync()

        tablet = harness.tablet_record(STAKE, 'st-1')
        server = harness.server_record(STAKE, 'st-1')

        assert tablet.data == server.data
        assert tablet.data['latitude'] == 49.5
        assert tablet.data['is_driven'] is True

    def test_alternating_updates(self) -> None:
        harness = SyncHarness()

        ts = harness.ts()
        harness.tablet_save(
            STAKE, 'st-1',
            {'id': 'st-1', 'latitude': 49.0},
            {'latitude': ts},
        )

        harness.sync()

        for i in range(5):
            ts = harness.ts()

            if i % 2 == 0:
                harness.tablet_save(
                    STAKE, 'st-1',
                    {'id': 'st-1', 'latitude': 49.0 + i},
                    {'latitude': ts},
                )
            else:
                harness.server_save(
                    STAKE, 'st-1',
                    {'id': 'st-1', 'latitude': 49.0 + i},
                    {'latitude': ts},
                )

            harness.sync()

            tablet = harness.tablet_record(STAKE, 'st-1')
            server = harness.server_record(STAKE, 'st-1')

            assert tablet.data == server.data

    def test_many_records_converge(self) -> None:
        harness = SyncHarness()

        for i in range(20):
            ts = harness.ts()

            if i % 2 == 0:
                harness.tablet_save(
                    STAKE, f'st-{i}',
                    {'id': f'st-{i}', 'latitude': 49.0 + i * 0.001},
                    {'latitude': ts},
                )
            else:
                harness.server_save(
                    STAKE, f'st-{i}',
                    {'id': f'st-{i}', 'latitude': 50.0 + i * 0.001},
                    {'latitude': ts},
                )

        harness.sync()

        for i in range(20):
            tablet = harness.tablet_record(STAKE, f'st-{i}')
            server = harness.server_record(STAKE, f'st-{i}')

            assert tablet is not None
            assert server is not None
            assert tablet.data == server.data


class TestRandomizedTwoPartyConvergence:
    @given(
        seed=st.integers(min_value=0, max_value=2**32),
        num_operations=st.integers(min_value=5, max_value=40),
    )
    @settings(max_examples=50, deadline=10_000)
    def test_random_create_and_update_converges(
        self,
        seed: int,
        num_operations: int,
    ) -> None:
        rng = random.Random(seed)
        harness = SyncHarness()
        keys = [f'st-{i}' for i in range(5)]

        for _ in range(num_operations):
            action = rng.choice(['tablet_write', 'server_write', 'sync'])

            if action == 'tablet_write':
                key = rng.choice(keys)
                ts = harness.ts()
                lat = rng.uniform(48.0, 52.0)

                harness.tablet_save(
                    STAKE, key,
                    {'id': key, 'latitude': lat},
                    {'latitude': ts},
                )
            elif action == 'server_write':
                key = rng.choice(keys)
                ts = harness.ts()
                lat = rng.uniform(48.0, 52.0)

                harness.server_save(
                    STAKE, key,
                    {'id': key, 'latitude': lat},
                    {'latitude': ts},
                )
            else:
                harness.sync()

        harness.sync()

        tablet_keys = set(harness.tablet_storage._records[STAKE].keys())
        server_keys = set(harness.server_storage._records[STAKE].keys())

        assert tablet_keys == server_keys

        for key in tablet_keys:
            tablet = harness.tablet_record(STAKE, key)
            server = harness.server_record(STAKE, key)

            assert tablet.data == server.data, (
                f'{key}: tablet={tablet.data} server={server.data}'
            )

    @given(
        seed=st.integers(min_value=0, max_value=2**32),
        num_operations=st.integers(min_value=5, max_value=30),
    )
    @settings(max_examples=50, deadline=10_000)
    def test_random_multi_field_convergence(
        self,
        seed: int,
        num_operations: int,
    ) -> None:
        rng = random.Random(seed)
        harness = SyncHarness()
        field_names = ['latitude', 'longitude', 'is_driven', 'is_reference']

        for _ in range(num_operations):
            action = rng.choice(['write', 'write', 'sync'])

            if action == 'write':
                key = rng.choice(['st-1', 'st-2', 'st-3'])
                side = rng.choice(['tablet', 'server'])
                fields_to_update = rng.sample(
                    field_names,
                    k=rng.randint(1, len(field_names)),
                )

                data: dict[str, Any] = {'id': key}
                timestamps: dict[str, int] = {}

                for field in fields_to_update:
                    ts = harness.ts()
                    data[field] = rng.uniform(-180, 180) if 'lat' in field or 'lon' in field else rng.choice([True, False])
                    timestamps[field] = ts

                storage = harness.tablet_storage if side == 'tablet' else harness.server_storage
                existing = storage._records[STAKE].get(key)

                if existing is not None:
                    merged_data = {**existing.data, **data}
                    merged_ts = {**existing.timestamps, **timestamps}
                else:
                    merged_data = data
                    merged_ts = timestamps

                if side == 'tablet':
                    harness.tablet_save(STAKE, key, merged_data, merged_ts)
                else:
                    harness.server_save(STAKE, key, merged_data, merged_ts)
            else:
                harness.sync()

        harness.sync()

        all_keys = set(harness.tablet_storage._records[STAKE]) | set(harness.server_storage._records[STAKE])

        for key in all_keys:
            tablet = harness.tablet_record(STAKE, key)
            server = harness.server_record(STAKE, key)

            assert tablet is not None, f'tablet missing {key}'
            assert server is not None, f'server missing {key}'
            assert tablet.data == server.data, (
                f'{key}: tablet={tablet.data} server={server.data}'
            )
