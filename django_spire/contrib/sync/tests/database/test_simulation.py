from __future__ import annotations

import pytest

from hypothesis import given, settings
from hypothesis import strategies as st

from django_spire.contrib.sync.tests.database.harness import ModelSchema
from django_spire.contrib.sync.tests.database.schemas import FLAT_SCHEMA, WIDE_SCHEMA
from django_spire.contrib.sync.tests.database.simulator import OpTag, SyncSimulator


class TestOracleConvergence:
    def test_single_tablet_single_write(self) -> None:
        sim = SyncSimulator(tablet_count=1, schemas=FLAT_SCHEMA, seed=1)
        sim.write_tablet('tablet_1', 'app.Record', 'r-1')
        sim.harness.sync_all_converge()
        sim.assert_converged_with_oracle()

    def test_two_tablets_disjoint_keys(self) -> None:
        sim = SyncSimulator(tablet_count=2, schemas=FLAT_SCHEMA, seed=1)
        sim.write_tablet('tablet_1', 'app.Record', 'r-1')
        sim.write_tablet('tablet_2', 'app.Record', 'r-2')
        sim.harness.sync_all_converge()
        sim.assert_converged_with_oracle()

    def test_tablet_and_server_write_same_key(self) -> None:
        sim = SyncSimulator(tablet_count=1, schemas=FLAT_SCHEMA, seed=1)
        sim.write_server('app.Record', 'r-1')
        sim.write_tablet('tablet_1', 'app.Record', 'r-1')
        sim.harness.sync_all_converge()
        sim.assert_converged_with_oracle()

    def test_three_tablets_write_same_key(self) -> None:
        sim = SyncSimulator(tablet_count=3, schemas=FLAT_SCHEMA, seed=1)
        for tablet_id in sim.tablet_ids:
            sim.write_tablet(tablet_id, 'app.Record', 'shared')
        sim.harness.sync_all_converge()
        sim.assert_converged_with_oracle()

    def test_field_level_lww_merge(self) -> None:
        sim = SyncSimulator(tablet_count=2, schemas=FLAT_SCHEMA, seed=1)

        ts_early = sim.harness.ts()
        ts_late = sim.harness.ts()

        sim.harness.tablet_save(
            'tablet_1', 'app.Record', 'r-1',
            {'id': 'r-1', 'name': 'tablet-1-name', 'value': 100},
            {'name': ts_late, 'value': ts_early},
        )
        sim.oracle.record_write(
            'app.Record', 'r-1',
            {'id': 'r-1', 'name': 'tablet-1-name', 'value': 100},
            {'name': ts_late, 'value': ts_early},
        )

        sim.harness.tablet_save(
            'tablet_2', 'app.Record', 'r-1',
            {'id': 'r-1', 'name': 'tablet-2-name', 'value': 200},
            {'name': ts_early, 'value': ts_late},
        )
        sim.oracle.record_write(
            'app.Record', 'r-1',
            {'id': 'r-1', 'name': 'tablet-2-name', 'value': 200},
            {'name': ts_early, 'value': ts_late},
        )

        sim.harness.sync_all_converge()
        sim.assert_converged_with_oracle()

        expected = sim.oracle.expected_data('app.Record', 'r-1')
        assert expected['name'] == 'tablet-1-name'
        assert expected['value'] == 200

    def test_many_writes_before_first_sync(self) -> None:
        sim = SyncSimulator(tablet_count=2, schemas=FLAT_SCHEMA, seed=1)

        for i in range(20):
            tablet_id = sim.tablet_ids[i % 2]
            sim.write_tablet(tablet_id, 'app.Record', f'r-{i % 5}')

        sim.harness.sync_all_converge()
        sim.assert_converged_with_oracle()


class TestCrashRecovery:
    def test_crash_single_tablet(self) -> None:
        sim = SyncSimulator(tablet_count=1, schemas=FLAT_SCHEMA, seed=1)

        sim.write_tablet('tablet_1', 'app.Record', 'r-1')
        sim.crash_mid_sync('tablet_1')

        sim.harness.sync_all_converge()
        sim.assert_converged_with_oracle()

    def test_crash_then_write_then_sync(self) -> None:
        sim = SyncSimulator(tablet_count=2, schemas=FLAT_SCHEMA, seed=1)

        sim.write_tablet('tablet_1', 'app.Record', 'r-1')
        sim.crash_mid_sync('tablet_1')

        sim.write_tablet('tablet_1', 'app.Record', 'r-2')

        sim.harness.sync_all_converge()
        sim.assert_converged_with_oracle()

    def test_crash_same_tablet_repeatedly(self) -> None:
        sim = SyncSimulator(tablet_count=2, schemas=FLAT_SCHEMA, seed=1)

        for i in range(5):
            sim.write_tablet('tablet_1', 'app.Record', f'r-{i}')
            sim.crash_mid_sync('tablet_1')

        sim.harness.sync_all_converge()
        sim.assert_converged_with_oracle()

    def test_crash_different_tablets(self) -> None:
        sim = SyncSimulator(tablet_count=3, schemas=FLAT_SCHEMA, seed=1)

        for tablet_id in sim.tablet_ids:
            sim.write_tablet(tablet_id, 'app.Record', 'r-1')

        sim.crash_mid_sync('tablet_1')
        sim.crash_mid_sync('tablet_3')

        sim.harness.sync_all_converge()
        sim.assert_converged_with_oracle()

    def test_crash_preserves_local_writes(self) -> None:
        sim = SyncSimulator(tablet_count=1, schemas=FLAT_SCHEMA, seed=1)

        sim.write_tablet('tablet_1', 'app.Record', 'r-1')

        before = dict(
            sim.harness.tablet_storages['tablet_1']._records['app.Record']['r-1'].data
        )

        sim.crash_mid_sync('tablet_1')

        after = dict(
            sim.harness.tablet_storages['tablet_1']._records['app.Record']['r-1'].data
        )

        assert before == after

    def test_crash_does_not_advance_checkpoint(self) -> None:
        sim = SyncSimulator(tablet_count=1, schemas=FLAT_SCHEMA, seed=1)

        sim.write_tablet('tablet_1', 'app.Record', 'r-1')

        checkpoint_before = sim.harness.tablet_storages['tablet_1'].get_checkpoint('tablet_1')
        sim.crash_mid_sync('tablet_1')
        checkpoint_after = sim.harness.tablet_storages['tablet_1'].get_checkpoint('tablet_1')

        assert checkpoint_before == checkpoint_after

    def test_server_receives_data_despite_crash(self) -> None:
        sim = SyncSimulator(tablet_count=1, schemas=FLAT_SCHEMA, seed=1)

        sim.write_tablet('tablet_1', 'app.Record', 'r-1')
        sim.crash_mid_sync('tablet_1')

        server_rec = sim.harness.server_record('app.Record', 'r-1')
        assert server_rec is not None


class TestIdempotency:
    def test_resync_after_crash_produces_same_result(self) -> None:
        sim = SyncSimulator(tablet_count=2, schemas=FLAT_SCHEMA, seed=1)

        sim.write_tablet('tablet_1', 'app.Record', 'r-1')
        sim.write_server('app.Record', 'r-2')

        sim.crash_mid_sync('tablet_1')

        sim.harness.sync_tablet('tablet_1')
        snapshot_first = dict(sim.harness.server_record('app.Record', 'r-1').data)

        sim.harness.sync_tablet('tablet_1')
        snapshot_second = dict(sim.harness.server_record('app.Record', 'r-1').data)

        assert snapshot_first == snapshot_second

    def test_ten_syncs_are_stable(self) -> None:
        sim = SyncSimulator(tablet_count=3, schemas=FLAT_SCHEMA, seed=1)

        for tablet_id in sim.tablet_ids:
            sim.write_tablet(tablet_id, 'app.Record', 'shared')

        sim.harness.sync_all_converge()
        snapshot = dict(sim.harness.server_record('app.Record', 'shared').data)

        for _ in range(10):
            sim.harness.sync_all()

        assert sim.harness.server_record('app.Record', 'shared').data == snapshot

    def test_timestamps_stable_across_idempotent_syncs(self) -> None:
        sim = SyncSimulator(tablet_count=2, schemas=FLAT_SCHEMA, seed=1)

        sim.write_tablet('tablet_1', 'app.Record', 'r-1')
        sim.harness.sync_all_converge()

        ts_before = dict(sim.harness.server_record('app.Record', 'r-1').timestamps)

        for _ in range(5):
            sim.harness.sync_all()

        ts_after = dict(sim.harness.server_record('app.Record', 'r-1').timestamps)
        assert ts_before == ts_after


class TestSwarmSimulation:
    @given(
        seed=st.integers(min_value=0, max_value=2**32),
        tablet_count=st.integers(min_value=1, max_value=5),
        num_operations=st.integers(min_value=10, max_value=80),
    )
    @settings(max_examples=50, deadline=15_000)
    def test_random_ops_converge_with_oracle(
        self,
        seed: int,
        tablet_count: int,
        num_operations: int,
    ) -> None:
        sim = SyncSimulator(
            tablet_count=tablet_count,
            schemas=FLAT_SCHEMA,
            seed=seed,
        )
        sim.run(num_operations)
        sim.assert_converged_with_oracle()

    @given(
        seed=st.integers(min_value=0, max_value=2**32),
        num_operations=st.integers(min_value=20, max_value=100),
    )
    @settings(max_examples=30, deadline=15_000)
    def test_crash_heavy_converges_with_oracle(
        self,
        seed: int,
        num_operations: int,
    ) -> None:
        sim = SyncSimulator(
            tablet_count=3,
            schemas=FLAT_SCHEMA,
            seed=seed,
        )
        sim._weights = {
            OpTag.WRITE_TABLET: 40,
            OpTag.WRITE_SERVER: 15,
            OpTag.SYNC_TABLET: 15,
            OpTag.SYNC_ALL: 5,
            OpTag.CRASH_MID_SYNC: 25,
        }
        sim.run(num_operations)
        sim.assert_converged_with_oracle()

    @given(
        seed=st.integers(min_value=0, max_value=2**32),
        num_fields=st.integers(min_value=1, max_value=20),
        num_keys=st.integers(min_value=1, max_value=15),
    )
    @settings(max_examples=30, deadline=15_000)
    def test_variable_schema_converges(
        self,
        seed: int,
        num_fields: int,
        num_keys: int,
    ) -> None:
        schemas = [
            ModelSchema(
                label='app.Dynamic',
                fields=[f'f_{i}' for i in range(num_fields)],
            ),
        ]
        sim = SyncSimulator(
            tablet_count=3,
            schemas=schemas,
            num_keys=num_keys,
            seed=seed,
        )
        sim.run(40)
        sim.assert_converged_with_oracle()

    @given(seed=st.integers(min_value=0, max_value=2**32))
    @settings(max_examples=20, deadline=15_000)
    def test_high_contention_single_key(self, seed: int) -> None:
        sim = SyncSimulator(
            tablet_count=5,
            schemas=FLAT_SCHEMA,
            num_keys=1,
            seed=seed,
        )
        sim.run(60)
        sim.assert_converged_with_oracle()

    @given(seed=st.integers(min_value=0, max_value=2**32))
    @settings(max_examples=20, deadline=15_000)
    def test_wide_schema_under_chaos(self, seed: int) -> None:
        sim = SyncSimulator(
            tablet_count=3,
            schemas=WIDE_SCHEMA,
            seed=seed,
        )
        sim._weights[OpTag.CRASH_MID_SYNC] = 10
        sim.run(50)
        sim.assert_converged_with_oracle()

    @given(seed=st.integers(min_value=0, max_value=2**32))
    @settings(max_examples=20, deadline=15_000)
    def test_write_heavy_no_sync_then_converge(self, seed: int) -> None:
        sim = SyncSimulator(
            tablet_count=4,
            schemas=FLAT_SCHEMA,
            seed=seed,
        )
        sim._weights = {
            OpTag.WRITE_TABLET: 100,
            OpTag.WRITE_SERVER: 30,
            OpTag.SYNC_TABLET: 0,
            OpTag.SYNC_ALL: 0,
            OpTag.CRASH_MID_SYNC: 0,
        }
        sim.run(80, converge=False)

        sim.harness.sync_all_converge(rounds=4)
        sim.assert_converged_with_oracle()

    @given(seed=st.integers(min_value=0, max_value=2**32))
    @settings(max_examples=20, deadline=15_000)
    def test_sync_heavy_with_sparse_writes(self, seed: int) -> None:
        sim = SyncSimulator(
            tablet_count=3,
            schemas=FLAT_SCHEMA,
            seed=seed,
        )
        sim._weights = {
            OpTag.WRITE_TABLET: 5,
            OpTag.WRITE_SERVER: 2,
            OpTag.SYNC_TABLET: 40,
            OpTag.SYNC_ALL: 20,
            OpTag.CRASH_MID_SYNC: 3,
        }
        sim.run(60)
        sim.assert_converged_with_oracle()


class TestScaleParameters:
    @pytest.mark.parametrize('tablet_count', [1, 2, 3, 5])
    def test_oracle_holds_across_tablet_counts(self, tablet_count: int) -> None:
        sim = SyncSimulator(
            tablet_count=tablet_count,
            schemas=FLAT_SCHEMA,
            seed=42,
        )
        sim.run(40)
        sim.assert_converged_with_oracle()

    @pytest.mark.parametrize('record_count', [1, 10, 50])
    def test_oracle_holds_across_record_counts(self, record_count: int) -> None:
        sim = SyncSimulator(
            tablet_count=2,
            schemas=FLAT_SCHEMA,
            num_keys=record_count,
            seed=42,
        )
        sim.run(60)
        sim.assert_converged_with_oracle()

    def test_twenty_field_schema(self) -> None:
        sim = SyncSimulator(
            tablet_count=3,
            schemas=WIDE_SCHEMA,
            seed=42,
        )
        sim.run(50)
        sim.assert_converged_with_oracle()

    def test_five_tablets_crash_heavy(self) -> None:
        sim = SyncSimulator(
            tablet_count=5,
            schemas=FLAT_SCHEMA,
            seed=42,
        )
        sim._weights[OpTag.CRASH_MID_SYNC] = 20
        sim.run(80)
        sim.assert_converged_with_oracle()
