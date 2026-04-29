from __future__ import annotations

from hypothesis import assume, given, settings
from hypothesis import strategies as st

from django_spire.contrib.sync.database.conflict import (
    RecordConflict,
    RecordResolution,
    ResolutionSource,
)
from django_spire.contrib.sync.database.manifest import ModelPayload
from django_spire.contrib.sync.database.reconciler import PayloadReconciler
from django_spire.contrib.sync.database.record import SyncRecord
from django_spire.contrib.sync.tests.database.strategies import reconciler_scenario


class TestReconcilerInvariants:
    @given(scenario=reconciler_scenario())
    @settings(max_examples=200, deadline=5_000)
    def test_new_records_always_created(
        self,
        scenario: tuple[dict, dict, int],
    ) -> None:
        local_records, remote_records, checkpoint = scenario

        remote_only_keys = set(remote_records.keys()) - set(local_records.keys())

        payload = ModelPayload(
            model_label='app.Model',
            records=remote_records,
        )

        reconciler = PayloadReconciler()
        result = reconciler.reconcile(payload, local_records, checkpoint)

        for key in remote_only_keys:
            assert key in result.created_keys, (
                f'Key {key!r} is remote-only but was not created'
            )
            assert key in result.to_upsert

    @given(scenario=reconciler_scenario())
    @settings(max_examples=200, deadline=5_000)
    def test_unchanged_local_records_always_applied(
        self,
        scenario: tuple[dict, dict, int],
    ) -> None:
        local_records, remote_records, checkpoint = scenario

        unchanged_keys = set()

        for key in set(local_records) & set(remote_records):
            if local_records[key].sync_field_last_modified <= checkpoint:
                unchanged_keys.add(key)

        payload = ModelPayload(
            model_label='app.Model',
            records=remote_records,
        )

        reconciler = PayloadReconciler()
        result = reconciler.reconcile(payload, local_records, checkpoint)

        for key in unchanged_keys:
            assert key in result.applied_keys, (
                f'Key {key!r} has sync_field_last_modified <= checkpoint '
                f'but was not applied'
            )

    @given(scenario=reconciler_scenario())
    @settings(max_examples=200, deadline=5_000)
    def test_all_remote_keys_accounted_for(
        self,
        scenario: tuple[dict, dict, int],
    ) -> None:
        local_records, remote_records, checkpoint = scenario

        payload = ModelPayload(
            model_label='app.Model',
            records=remote_records,
        )

        reconciler = PayloadReconciler()
        result = reconciler.reconcile(payload, local_records, checkpoint)

        accounted = (
            result.created_keys
            | result.applied_keys
            | set(result.conflict_keys)
            | set(result.compatible_keys)
            | {e.key for e in result.errors}
        )

        for key in remote_records:
            assert key in accounted, (
                f'Key {key!r} was in remote records but not accounted '
                f'for in any result category'
            )

    @given(scenario=reconciler_scenario())
    @settings(max_examples=200, deadline=5_000)
    def test_no_key_appears_in_multiple_categories(
        self,
        scenario: tuple[dict, dict, int],
    ) -> None:
        local_records, remote_records, checkpoint = scenario

        payload = ModelPayload(
            model_label='app.Model',
            records=remote_records,
        )

        reconciler = PayloadReconciler()
        result = reconciler.reconcile(payload, local_records, checkpoint)

        created = result.created_keys
        applied = result.applied_keys
        conflict = set(result.conflict_keys)
        compatible = set(result.compatible_keys)

        all_sets = [created, applied, conflict, compatible]

        for i, set_a in enumerate(all_sets):
            for j, set_b in enumerate(all_sets):
                if i != j:
                    overlap = set_a & set_b
                    assert not overlap, (
                        f'Keys {overlap} appear in multiple categories'
                    )

    @given(scenario=reconciler_scenario())
    @settings(max_examples=200, deadline=5_000)
    def test_upsert_keys_are_subset_of_created_plus_applied_plus_resolved(
        self,
        scenario: tuple[dict, dict, int],
    ) -> None:
        local_records, remote_records, checkpoint = scenario

        payload = ModelPayload(
            model_label='app.Model',
            records=remote_records,
        )

        reconciler = PayloadReconciler()
        result = reconciler.reconcile(payload, local_records, checkpoint)

        expected_upsert_sources = (
            result.created_keys
            | result.applied_keys
            | set(result.conflict_keys)
            | set(result.compatible_keys)
        )

        for key in result.to_upsert:
            assert key in expected_upsert_sources, (
                f'Key {key!r} is in to_upsert but not in any source category'
            )

    @given(
        checkpoint=st.integers(min_value=50, max_value=500),
        num_keys=st.integers(min_value=1, max_value=5),
    )
    @settings(max_examples=100, deadline=5_000)
    def test_delete_of_unchanged_record_is_accepted(
        self,
        checkpoint: int,
        num_keys: int,
    ) -> None:
        local_records: dict[str, SyncRecord] = {}
        deletes: dict[str, int] = {}

        for i in range(num_keys):
            key = str(i)
            local_ts = checkpoint - 10

            local_records[key] = SyncRecord(
                key=key,
                data={'id': key, 'name': f'record-{i}'},
                timestamps={'name': local_ts},
            )
            deletes[key] = checkpoint

        payload = ModelPayload(
            model_label='app.Model',
            records={},
            deletes=deletes,
        )

        reconciler = PayloadReconciler()
        result = reconciler.reconcile(payload, local_records, checkpoint)

        for key in local_records:
            assert key in result.to_delete, (
                f'Key {key!r} is unchanged (sync_field_last_modified <= tombstone) '
                f'but delete was not accepted'
            )

    @given(scenario=reconciler_scenario())
    @settings(max_examples=100, deadline=5_000)
    def test_delete_of_nonexistent_key_is_noop(
        self,
        scenario: tuple[dict, dict, int],
    ) -> None:
        local_records, _, checkpoint = scenario

        phantom_keys = {f'phantom-{i}' for i in range(3)}
        phantom_keys -= set(local_records.keys())

        assume(len(phantom_keys) > 0)

        deletes = dict.fromkeys(phantom_keys, checkpoint + 1000)

        payload = ModelPayload(
            model_label='app.Model',
            records={},
            deletes=deletes,
        )

        reconciler = PayloadReconciler()
        result = reconciler.reconcile(payload, local_records, checkpoint)

        assert result.to_delete == {}
        assert not result.errors


        class _ExplodingDeleteResolver:
            def resolve(self, conflict: RecordConflict) -> RecordResolution:
                _ = conflict

                message = 'resolver exploded'
                raise RuntimeError(message)


        def test_delete_conflict_resolver_exception_recorded() -> None:
            local_records = {
                '1': SyncRecord(
                    key='1',
                    data={'id': '1', 'name': 'modified'},
                    timestamps={'name': 150},
                ),
            }

            payload = ModelPayload(
                model_label='app.Model',
                records={},
                deletes={'1': 100},
            )

            reconciler = PayloadReconciler(resolver=_ExplodingDeleteResolver())
            result = reconciler.reconcile(payload, local_records, checkpoint=50)

            assert len(result.errors) == 1
            assert result.errors[0].key == '1'
            assert 'resolver exploded' in result.errors[0].message


class _DeleteAcceptResolver:
    def resolve(self, conflict: RecordConflict) -> RecordResolution:
        _ = conflict

        return RecordResolution(
            record=None,
            source=ResolutionSource.REMOTE,
            delete=True,
        )


def test_delete_conflict_resolver_accepts_delete() -> None:
    local_records = {
        '1': SyncRecord(
            key='1',
            data={'id': '1', 'name': 'modified'},
            timestamps={'name': 150},
        ),
    }

    payload = ModelPayload(
        model_label='app.Model',
        records={},
        deletes={'1': 100},
    )

    reconciler = PayloadReconciler(resolver=_DeleteAcceptResolver())
    result = reconciler.reconcile(payload, local_records, checkpoint=50)

    assert '1' in result.to_delete
    assert len(result.errors) == 0


class _DeleteRejectResolver:
    def resolve(self, conflict: RecordConflict) -> RecordResolution:
        return RecordResolution(
            record=conflict.local,
            source=ResolutionSource.LOCAL,
            delete=False,
        )


def test_delete_conflict_resolver_keeps_record() -> None:
    local = SyncRecord(
        key='1',
        data={'id': '1', 'name': 'keep-me'},
        timestamps={'name': 150},
    )

    local_records = {'1': local}

    payload = ModelPayload(
        model_label='app.Model',
        records={},
        deletes={'1': 100},
    )

    reconciler = PayloadReconciler(resolver=_DeleteRejectResolver())
    result = reconciler.reconcile(payload, local_records, checkpoint=50)

    assert '1' not in result.to_delete
    assert '1' in result.response_records
    assert result.response_records['1'].data['name'] == 'keep-me'


def test_delete_nonexistent_key_skipped() -> None:
    payload = ModelPayload(
        model_label='app.Model',
        records={},
        deletes={'ghost': 500},
    )

    reconciler = PayloadReconciler()
    result = reconciler.reconcile(payload, {}, checkpoint=100)

    assert 'ghost' not in result.to_delete
    assert len(result.errors) == 0


def test_delete_unchanged_record_accepted() -> None:
    local_records = {
        '1': SyncRecord(
            key='1',
            data={'id': '1', 'name': 'old'},
            timestamps={'name': 50},
        ),
    }

    payload = ModelPayload(
        model_label='app.Model',
        records={},
        deletes={'1': 100},
    )

    reconciler = PayloadReconciler()
    result = reconciler.reconcile(payload, local_records, checkpoint=0)

    assert '1' in result.to_delete
