from __future__ import annotations

import string

from typing import Any

from hypothesis import assume, given, settings
from hypothesis import strategies as st

from django_spire.contrib.sync.core.clock import HybridLogicalClock
from django_spire.contrib.sync.core.hash import RecordHasher
from django_spire.contrib.sync.database.conflict import (
    ConflictType,
    FieldOwnershipWins,
    FieldTimestampWins,
    LocalWins,
    RecordConflict,
    RemoteWins,
    ResolutionSource,
)
from django_spire.contrib.sync.database.manifest import (
    ModelPayload,
    SyncManifest,
)
from django_spire.contrib.sync.database.record import SyncRecord
from django_spire.contrib.sync.tests.database.strategies import (
    DATA_DICTS,
    field_conflict_pairs,
    sync_manifests,
    sync_records,
)


class TestClockMonotonicity:
    @given(count=st.integers(min_value=2, max_value=200))
    @settings(max_examples=50)
    def test_now_strictly_monotonic(self, count: int) -> None:
        clock = HybridLogicalClock()
        clock._physical = lambda: 1000

        timestamps = [clock.now() for _ in range(count)]

        assert timestamps == sorted(timestamps)
        assert len(set(timestamps)) == len(timestamps)

    @given(
        remote_wall=st.integers(min_value=1, max_value=2**40),
        remote_counter=st.integers(min_value=0, max_value=100),
    )
    @settings(max_examples=100)
    def test_receive_always_advances(
        self,
        remote_wall: int,
        remote_counter: int,
    ) -> None:
        clock = HybridLogicalClock()
        clock._physical = lambda: 1000

        before = clock.now()
        remote = (remote_wall << 16) | remote_counter
        after = clock.receive(remote)

        assert after > before
        assert after > remote

    @given(
        physical_times=st.lists(
            st.integers(min_value=1, max_value=100_000),
            min_size=3,
            max_size=20,
        ),
    )
    @settings(max_examples=50)
    def test_never_goes_backward_with_wall_clock_jitter(
        self,
        physical_times: list[int],
    ) -> None:
        clock = HybridLogicalClock()
        idx = [0]

        def jittery_physical() -> int:
            t = physical_times[idx[0] % len(physical_times)]
            idx[0] += 1
            return t

        clock._physical = jittery_physical

        previous = 0

        for _ in range(len(physical_times)):
            ts = clock.now()
            assert ts > previous
            previous = ts

    @given(
        remotes=st.lists(
            st.builds(
                lambda wall, counter: (wall << 16) | counter,
                wall=st.integers(min_value=1, max_value=2**34),
                counter=st.integers(min_value=0, max_value=1000),
            ),
            min_size=2,
            max_size=10,
        ),
    )
    @settings(max_examples=50)
    def test_receive_sequence_always_monotonic(
        self,
        remotes: list[int],
    ) -> None:
        clock = HybridLogicalClock()

        previous = 0

        for remote in remotes:
            result = clock.receive(remote)
            assert result > previous
            previous = result

    @given(
        remote_a=st.integers(min_value=1, max_value=2**50),
        remote_b=st.integers(min_value=1, max_value=2**50),
    )
    @settings(max_examples=100)
    def test_two_clocks_converge_past_both(
        self,
        remote_a: int,
        remote_b: int,
    ) -> None:
        _ = remote_a
        _ = remote_b

        clock_a = HybridLogicalClock()
        clock_b = HybridLogicalClock()
        clock_a._physical = lambda: 1000
        clock_b._physical = lambda: 1000

        ts_a = clock_a.now()
        ts_b = clock_b.now()

        after_a = clock_a.receive(ts_b)
        after_b = clock_b.receive(ts_a)

        assert after_a > ts_a
        assert after_a > ts_b
        assert after_b > ts_a
        assert after_b > ts_b


class TestManifestRoundTrip:
    @given(manifest=sync_manifests())
    @settings(max_examples=100)
    def test_to_dict_from_dict_preserves_node_id(
        self,
        manifest: SyncManifest,
    ) -> None:
        restored = SyncManifest.from_dict(manifest.to_dict())

        assert restored.node_id == manifest.node_id

    @given(manifest=sync_manifests())
    @settings(max_examples=100)
    def test_to_dict_from_dict_preserves_checkpoint(
        self,
        manifest: SyncManifest,
    ) -> None:
        restored = SyncManifest.from_dict(manifest.to_dict())

        assert restored.checkpoint == manifest.checkpoint

    @given(manifest=sync_manifests())
    @settings(max_examples=100)
    def test_to_dict_from_dict_preserves_payload_count(
        self,
        manifest: SyncManifest,
    ) -> None:
        restored = SyncManifest.from_dict(manifest.to_dict())

        assert len(restored.payloads) == len(manifest.payloads)

    @given(manifest=sync_manifests())
    @settings(max_examples=100)
    def test_to_dict_from_dict_preserves_record_keys(
        self,
        manifest: SyncManifest,
    ) -> None:
        restored = SyncManifest.from_dict(manifest.to_dict())

        for original_payload, restored_payload in zip(
            manifest.payloads, restored.payloads, strict=False,
        ):
            assert set(restored_payload.records.keys()) == set(original_payload.records.keys())

    @given(manifest=sync_manifests())
    @settings(max_examples=100)
    def test_to_dict_from_dict_preserves_deletes(
        self,
        manifest: SyncManifest,
    ) -> None:
        restored = SyncManifest.from_dict(manifest.to_dict())

        for original_payload, restored_payload in zip(
            manifest.payloads, restored.payloads, strict=False,
        ):
            assert restored_payload.deletes == original_payload.deletes

    @given(manifest=sync_manifests())
    @settings(max_examples=100)
    def test_to_dict_from_dict_preserves_record_data(
        self,
        manifest: SyncManifest,
    ) -> None:
        restored = SyncManifest.from_dict(manifest.to_dict())

        for original_payload, restored_payload in zip(
            manifest.payloads, restored.payloads, strict=False,
        ):
            for key in original_payload.records:
                original = original_payload.records[key]
                result = restored_payload.records[key]

                assert result.data == original.data
                assert result.timestamps == original.timestamps

    @given(manifest=sync_manifests())
    @settings(max_examples=100)
    def test_checksum_is_deterministic(
        self,
        manifest: SyncManifest,
    ) -> None:
        a = manifest.compute_checksum()
        b = manifest.compute_checksum()

        assert a == b

    @given(manifest=sync_manifests())
    @settings(max_examples=100)
    def test_to_dict_always_produces_valid_checksum(
        self,
        manifest: SyncManifest,
    ) -> None:
        data = manifest.to_dict()
        restored = SyncManifest.from_dict(data)

        assert restored.verify() is True

    @given(
        manifest=sync_manifests(),
        extra_key=st.text(alphabet=string.ascii_lowercase, min_size=1, max_size=5),
    )
    @settings(max_examples=50)
    def test_checksum_changes_when_data_changes(
        self,
        manifest: SyncManifest,
        extra_key: str,
    ) -> None:
        existing_labels = {p.model_label for p in manifest.payloads}
        injected_label = 'injected.Model'

        assume(injected_label not in existing_labels)

        checksum_before = manifest.compute_checksum()

        modified = SyncManifest(
            node_id=manifest.node_id,
            checkpoint=manifest.checkpoint,
            node_time=manifest.node_time,
            payloads=[
                *manifest.payloads,
                ModelPayload(
                    model_label=injected_label,
                    records={
                        extra_key: SyncRecord(
                            key=extra_key,
                            data={'id': extra_key, 'injected': True},
                            timestamps={'injected': 999}
                        )
                    }
                )
            ],
        )

        checksum_after = modified.compute_checksum()

        assert checksum_before != checksum_after


class TestSyncRecordRoundTrip:
    @given(record=sync_records())
    @settings(max_examples=100)
    def test_to_dict_from_dict_preserves_data(
        self,
        record: SyncRecord,
    ) -> None:
        restored = SyncRecord.from_dict(record.key, record.to_dict())

        assert restored.data == record.data
        assert restored.timestamps == record.timestamps

    @given(record=sync_records())
    @settings(max_examples=100)
    def test_sync_field_last_modified_equals_max_timestamp(
        self,
        record: SyncRecord,
    ) -> None:
        if record.timestamps:
            assert record.sync_field_last_modified == max(record.timestamps.values())
        else:
            assert record.sync_field_last_modified == 0


class TestHasherProperties:
    @given(data=DATA_DICTS)
    @settings(max_examples=100)
    def test_hash_is_deterministic(self, data: dict[str, Any]) -> None:
        data['id'] = '1'
        hasher = RecordHasher(identity_field='id')

        assert hasher.hash(data) == hasher.hash(data)

    @given(data=DATA_DICTS)
    @settings(max_examples=100)
    def test_hash_ignores_field_order(self, data: dict[str, Any]) -> None:
        data['id'] = '1'
        hasher = RecordHasher(identity_field='id')

        reversed_data = dict(reversed(list(data.items())))

        assert hasher.hash(data) == hasher.hash(reversed_data)

    @given(data=DATA_DICTS, id_a=st.text(min_size=1, max_size=5), id_b=st.text(min_size=1, max_size=5))
    @settings(max_examples=100)
    def test_hash_ignores_identity_field(
        self,
        data: dict[str, Any],
        id_a: str,
        id_b: str,
    ) -> None:
        hasher = RecordHasher(identity_field='id')

        a = {**data, 'id': id_a}
        b = {**data, 'id': id_b}

        assert hasher.hash(a) == hasher.hash(b)


class TestFieldTimestampWinsProperties:
    @given(pair=field_conflict_pairs())
    @settings(max_examples=200)
    def test_merged_record_contains_all_non_meta_fields(
        self,
        pair: tuple[dict, dict, dict, dict],
    ) -> None:
        local_data, remote_data, local_ts, remote_ts = pair

        local = SyncRecord(key='1', data=local_data, timestamps=local_ts)
        remote = SyncRecord(key='1', data=remote_data, timestamps=remote_ts)

        conflict = RecordConflict(
            key='1',
            model_label='app.Model',
            conflict_type=ConflictType.BOTH_MODIFIED,
            local=local,
            remote=remote,
        )

        resolution = FieldTimestampWins().resolve(conflict)

        assert resolution.record is not None

        expected_fields = (
            (set(local_data) | set(remote_data))
            - {'sync_field_timestamps', 'sync_field_last_modified'}
        )

        assert set(resolution.record.data.keys()) == expected_fields

    @given(pair=field_conflict_pairs())
    @settings(max_examples=200)
    def test_merged_timestamps_are_elementwise_max(
        self,
        pair: tuple[dict, dict, dict, dict],
    ) -> None:
        local_data, remote_data, local_ts, remote_ts = pair

        local = SyncRecord(key='1', data=local_data, timestamps=local_ts)
        remote = SyncRecord(key='1', data=remote_data, timestamps=remote_ts)

        conflict = RecordConflict(
            key='1',
            model_label='app.Model',
            conflict_type=ConflictType.BOTH_MODIFIED,
            local=local,
            remote=remote,
        )

        resolution = FieldTimestampWins().resolve(conflict)

        assert resolution.record is not None

        for field, ts in resolution.record.timestamps.items():
            if field in {'sync_field_timestamps', 'sync_field_last_modified'}:
                continue

            local_t = local_ts.get(field, 0)
            remote_t = remote_ts.get(field, 0)

            assert ts == max(local_t, remote_t)

    @given(pair=field_conflict_pairs())
    @settings(max_examples=200)
    def test_winning_value_comes_from_higher_timestamp_side(
        self,
        pair: tuple[dict, dict, dict, dict],
    ) -> None:
        local_data, remote_data, local_ts, remote_ts = pair

        local = SyncRecord(key='1', data=local_data, timestamps=local_ts)
        remote = SyncRecord(key='1', data=remote_data, timestamps=remote_ts)

        conflict = RecordConflict(
            key='1',
            model_label='app.Model',
            conflict_type=ConflictType.BOTH_MODIFIED,
            local=local,
            remote=remote,
        )

        resolution = FieldTimestampWins().resolve(conflict)

        assert resolution.record is not None

        meta = {'sync_field_timestamps', 'sync_field_last_modified'}

        for field in resolution.record.data:
            if field in meta:
                continue

            local_t = local_ts.get(field, 0)
            remote_t = remote_ts.get(field, 0)

            if remote_t > local_t:
                assert resolution.record.data[field] == remote_data.get(field)
            else:
                assert resolution.record.data[field] == local_data.get(field)

    @given(pair=field_conflict_pairs())
    @settings(max_examples=100)
    def test_prefer_remote_on_tie_flips_tie_behavior(
        self,
        pair: tuple[dict, dict, dict, dict],
    ) -> None:
        local_data, remote_data, local_ts, remote_ts = pair

        tied_ts = 500
        shared_fields = set(local_data) & set(remote_data) - {'id', 'sync_field_timestamps', 'sync_field_last_modified'}

        assume(len(shared_fields) > 0)

        field = sorted(shared_fields)[0]

        local_ts_tied = {**local_ts, field: tied_ts}
        remote_ts_tied = {**remote_ts, field: tied_ts}

        local = SyncRecord(key='1', data=local_data, timestamps=local_ts_tied)
        remote = SyncRecord(key='1', data=remote_data, timestamps=remote_ts_tied)

        conflict = RecordConflict(
            key='1',
            model_label='app.Model',
            conflict_type=ConflictType.BOTH_MODIFIED,
            local=local,
            remote=remote,
        )

        default_resolution = FieldTimestampWins().resolve(conflict)
        remote_preferred = FieldTimestampWins(prefer_remote_on_tie=True).resolve(conflict)

        assert default_resolution.record is not None
        assert remote_preferred.record is not None

        assert default_resolution.record.data[field] == local_data[field]
        assert remote_preferred.record.data[field] == remote_data[field]


class TestFieldOwnershipWinsProperties:
    @given(pair=field_conflict_pairs())
    @settings(max_examples=200)
    def test_owned_fields_always_come_from_owner(
        self,
        pair: tuple[dict, dict, dict, dict],
    ) -> None:
        local_data, remote_data, local_ts, remote_ts = pair

        all_fields = (
            (set(local_data) | set(remote_data))
            - {'id', 'sync_field_timestamps', 'sync_field_last_modified'}
        )

        assume(len(all_fields) >= 2)

        sorted_fields = sorted(all_fields)
        midpoint = len(sorted_fields) // 2
        local_owned = set(sorted_fields[:midpoint])
        remote_owned = set(sorted_fields[midpoint:])

        local = SyncRecord(key='1', data=local_data, timestamps=local_ts)
        remote = SyncRecord(key='1', data=remote_data, timestamps=remote_ts)

        conflict = RecordConflict(
            key='1',
            model_label='app.Model',
            conflict_type=ConflictType.BOTH_MODIFIED,
            local=local,
            remote=remote,
        )

        resolution = FieldOwnershipWins(
            local_fields=local_owned,
            remote_fields=remote_owned,
        ).resolve(conflict)

        assert resolution.record is not None

        for field in local_owned:
            if field in resolution.record.data:
                assert resolution.record.data[field] == local_data.get(field)

        for field in remote_owned:
            if field in resolution.record.data:
                assert resolution.record.data[field] == remote_data.get(field)


class TestLocalRemoteWinsDuality:
    @given(pair=field_conflict_pairs())
    @settings(max_examples=100)
    def test_local_wins_always_returns_local(
        self,
        pair: tuple[dict, dict, dict, dict],
    ) -> None:
        local_data, remote_data, local_ts, remote_ts = pair

        local = SyncRecord(key='1', data=local_data, timestamps=local_ts)
        remote = SyncRecord(key='1', data=remote_data, timestamps=remote_ts)

        conflict = RecordConflict(
            key='1',
            model_label='app.Model',
            conflict_type=ConflictType.BOTH_MODIFIED,
            local=local,
            remote=remote,
        )

        resolution = LocalWins().resolve(conflict)

        assert resolution.record is not None
        assert resolution.record.data == local_data
        assert resolution.source == ResolutionSource.LOCAL

    @given(pair=field_conflict_pairs())
    @settings(max_examples=100)
    def test_remote_wins_always_returns_remote(
        self,
        pair: tuple[dict, dict, dict, dict],
    ) -> None:
        local_data, remote_data, local_ts, remote_ts = pair

        local = SyncRecord(key='1', data=local_data, timestamps=local_ts)
        remote = SyncRecord(key='1', data=remote_data, timestamps=remote_ts)

        conflict = RecordConflict(
            key='1',
            model_label='app.Model',
            conflict_type=ConflictType.BOTH_MODIFIED,
            local=local,
            remote=remote,
        )

        resolution = RemoteWins().resolve(conflict)

        assert resolution.record is not None
        assert resolution.record.data == remote_data
        assert resolution.source == ResolutionSource.REMOTE

    def test_local_wins_modify_vs_delete_deletes(self) -> None:
        local = SyncRecord(key='1', data={'id': '1'}, timestamps={'id': 100})

        conflict = RecordConflict(
            key='1',
            model_label='app.Model',
            conflict_type=ConflictType.MODIFY_VS_DELETE,
            local=local,
        )

        resolution = LocalWins().resolve(conflict)

        assert resolution.delete is True
        assert resolution.record is None

    def test_remote_wins_delete_vs_modify_deletes(self) -> None:
        remote = SyncRecord(key='1', data={'id': '1'}, timestamps={'id': 100})

        conflict = RecordConflict(
            key='1',
            model_label='app.Model',
            conflict_type=ConflictType.DELETE_VS_MODIFY,
            local=remote,
        )

        resolution = RemoteWins().resolve(conflict)

        assert resolution.delete is True
        assert resolution.record is None
