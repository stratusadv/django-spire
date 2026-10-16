from __future__ import annotations

import time
from typing import Any, Callable
from unittest.mock import MagicMock, patch

import pytest
from celery import states
from django.test import SimpleTestCase
from pydantic import ValidationError

from django_spire.celery.meta import CeleryTaskMeta, TaskDataModel, derive_final_meta_key
from django_spire.celery.tracker import CeleryTaskTracker


class _CountedData(TaskDataModel):
    counted_seconds: int | None = None


def _make_task() -> MagicMock:
    task = MagicMock()
    task.request.id = 'test-task-id'
    task.backend = MagicMock()
    return task


def _make_untracked_task() -> MagicMock:
    task = MagicMock()
    task.request.id = None
    task.backend = MagicMock()
    return task


class CeleryTaskTrackerConstructionTestCase(SimpleTestCase):
    def test_requires_minimum_update_interval(self) -> None:
        task = _make_task()

        with pytest.raises(ValueError, match='Update Interval'):
            CeleryTaskTracker(task, update_interval_seconds=4)

    def test_accepts_update_interval_of_five(self) -> None:
        task = _make_task()
        tracker = CeleryTaskTracker(task, update_interval_seconds=5)
        assert tracker._update_interval_seconds == 5

    def test_exposes_celery_task(self) -> None:
        task = _make_task()
        tracker = CeleryTaskTracker(task)
        assert tracker.task is task


class CeleryTaskTrackerUntrackedTestCase(SimpleTestCase):
    def test_update_state_uppercases_state(self) -> None:
        tracker = CeleryTaskTracker(_make_untracked_task())

        tracker.update_state('making noises')

        assert tracker._state == 'MAKING NOISES'

    def test_update_state_truncates_long_state(self) -> None:
        tracker = CeleryTaskTracker(_make_untracked_task())

        tracker.update_state('MAKING' * 10)

        assert len(tracker._state) == 32
        assert tracker._state.endswith(' ...')

    def test_update_state_does_not_start_flusher(self) -> None:
        task = _make_untracked_task()
        tracker = CeleryTaskTracker(task)

        tracker.update_state('MAKING NOISES')

        assert tracker._flusher is None
        task.backend.store_result.assert_not_called()

    def test_set_completed_marks_meta_without_writing(self) -> None:
        task = _make_untracked_task()
        tracker = CeleryTaskTracker(task)

        tracker.set_completed()

        assert tracker.meta.progress == 1.0
        assert tracker.meta.completed_time is not None
        task.backend.store_result.assert_not_called()

    def test_meta_data_set_without_model_does_not_write(self) -> None:
        task = _make_untracked_task()
        tracker = CeleryTaskTracker(task)

        tracker.meta.data['counted_seconds'] = 3

        assert tracker.meta.data == {'counted_seconds': 3}
        task.backend.store_result.assert_not_called()

    def test_set_retries_updates_meta(self) -> None:
        tracker = CeleryTaskTracker(_make_untracked_task())

        tracker.set_retries(2)

        assert tracker.meta.retries == 2

    def test_finish_success_untracked_does_not_raise(self) -> None:
        tracker = CeleryTaskTracker(_make_untracked_task())

        tracker.finish(states.SUCCESS)

    def test_finish_failure_untracked_does_not_raise(self) -> None:
        tracker = CeleryTaskTracker(_make_untracked_task())

        tracker.finish(states.FAILURE, exc=ValueError('boom'))


class CeleryTaskTrackerProgressTestCase(SimpleTestCase):
    def test_update_count_progress_sets_progress(self) -> None:
        tracker = CeleryTaskTracker(_make_untracked_task())
        tracker.meta.last_update_time = 0
        tracker.meta.set_started()

        tracker.update_count_progress(5, 10)

        assert tracker.meta.progress == 0.5

    def test_update_count_progress_validates_range(self) -> None:
        tracker = CeleryTaskTracker(_make_untracked_task())

        with pytest.raises(ValueError, match='Progress range is invalid'):
            tracker.update_count_progress(1, 10, range_min=2.0, range_max=1.0)

    def test_update_count_progress_zero_target_raises(self) -> None:
        tracker = CeleryTaskTracker(_make_untracked_task())

        with pytest.raises(ValueError, match='non-zero'):
            tracker.update_count_progress(1, 0)

    def test_update_cumulative_progress_without_target_raises(self) -> None:
        tracker = CeleryTaskTracker(_make_untracked_task())

        with pytest.raises(ValueError, match='Cumulative Progress Target Value'):
            tracker.update_cumulative_progress(1)

    def test_update_cumulative_progress_sets_progress(self) -> None:
        tracker = CeleryTaskTracker(_make_untracked_task())
        tracker.meta.last_update_time = 0
        tracker.meta.set_started()
        tracker.set_cumulative_progress_target_value(10)

        tracker.update_cumulative_progress(3)

        assert tracker.meta.progress == 0.3


class CeleryTaskTrackerMetaDataModelTestCase(SimpleTestCase):
    def test_typed_meta_data_is_a_model_instance(self) -> None:
        tracker = CeleryTaskTracker(_make_untracked_task(), meta_data_model=_CountedData)

        assert isinstance(tracker.meta.data, _CountedData)

    def test_typed_meta_data_validates_assignment(self) -> None:
        tracker = CeleryTaskTracker(_make_untracked_task(), meta_data_model=_CountedData)

        with pytest.raises(ValidationError):
            tracker.meta.data.counted_seconds = 'not-an-int'

    def test_typed_meta_data_set_schedules_update(self) -> None:
        tracker = CeleryTaskTracker(_make_task(), meta_data_model=_CountedData)

        with patch.object(CeleryTaskTracker, '_ensure_flusher'):
            tracker.meta.data.counted_seconds = 3

        assert tracker._pending_snapshot is not None
        assert tracker._pending_snapshot.meta_dict['data'] == {'counted_seconds': 3}

    def test_free_form_meta_data_without_meta_data_model(self) -> None:
        tracker = CeleryTaskTracker(_make_untracked_task())

        tracker.meta.data['bananas'] = 'key'

        assert tracker.meta.data == {'bananas': 'key'}


class CeleryTaskMetaTestCase(SimpleTestCase):
    def test_estimated_run_time_seconds_uses_started_time(self) -> None:
        meta = CeleryTaskMeta(started_time=100.0, estimated_completed_time=160.0)

        assert meta.estimated_run_time_seconds == 60.0

    def test_estimated_run_time_seconds_none_without_estimates(self) -> None:
        meta = CeleryTaskMeta(started_time=100.0)

        assert meta.estimated_run_time_seconds is None

    def test_set_completed_sets_progress_and_completed_time(self) -> None:
        meta = CeleryTaskMeta()
        meta.set_completed()

        assert meta.progress == 1.0
        assert meta.completed_time is not None

    def test_set_started_sets_progress_and_started_time(self) -> None:
        meta = CeleryTaskMeta()
        meta.set_started()

        assert meta.progress == 0.02
        assert meta.started_time is not None

    def test_set_started_and_completing_soon_sets_estimate(self) -> None:
        meta = CeleryTaskMeta()
        meta.set_started_and_completing_soon()

        assert meta.progress == 1.0
        assert meta.estimated_completed_time is not None

    def test_set_started_and_completing_soon_last_update_not_in_future(self) -> None:
        meta = CeleryTaskMeta()
        meta.set_started_and_completing_soon()

        assert meta.last_update_time <= time.time()

    def test_set_failed_sets_error_without_touching_progress(self) -> None:
        meta = CeleryTaskMeta(progress=0.4)
        meta.set_failed('ValueError: boom')

        assert meta.error == 'ValueError: boom'
        assert meta.failed_time is not None
        assert meta.progress == 0.4
        assert meta.completed_time is None

    def test_merge_keeps_extra_fields(self) -> None:
        base = CeleryTaskMeta()
        other = CeleryTaskMeta(worker_hostname='host-1')

        base.merge(other)

        assert base.model_dump()['worker_hostname'] == 'host-1'

    def test_merge_deep_merges_data(self) -> None:
        base = CeleryTaskMeta(data={'more': {'has_noises': True}, 'bananas': 'key'})
        other = CeleryTaskMeta(data={'more': {'level': 2}, 'counted_seconds': 3})

        base.merge(other)

        assert base.data == {
            'more': {'has_noises': True, 'level': 2},
            'bananas': 'key',
            'counted_seconds': 3,
        }

    def test_merge_skips_none_values(self) -> None:
        base = CeleryTaskMeta(progress=0.5, started_time=100.0)
        other = CeleryTaskMeta()

        base.merge(other)

        assert base.progress == 0.5
        assert base.started_time == 100.0

    def test_model_dump_excludes_progress_updates_count(self) -> None:
        meta = CeleryTaskMeta()
        dumped = meta.model_dump()

        assert '_progress_updates_count' not in dumped
        assert dumped['data'] == {}
        assert dumped['progress'] is None

    def test_model_dump_includes_retries_error_failed_time(self) -> None:
        meta = CeleryTaskMeta(retries=2, error='boom', failed_time=123.0)
        dumped = meta.model_dump()

        assert dumped['retries'] == 2
        assert dumped['error'] == 'boom'
        assert dumped['failed_time'] == 123.0

    def test_default_data_field_is_isolated_per_instance(self) -> None:
        first = CeleryTaskMeta()
        second = CeleryTaskMeta()
        first.data['key'] = 'value'

        assert second.data == {}

    def test_untyped_meta_accepts_wire_dict_data(self) -> None:
        meta = CeleryTaskMeta(data={'counted_seconds': 3}, progress=0.5)

        assert meta.data == {'counted_seconds': 3}
        assert isinstance(meta.data, dict)

    def test_parameterized_meta_holds_typed_data(self) -> None:
        meta = CeleryTaskMeta[_CountedData](data=_CountedData(counted_seconds=3))

        assert isinstance(meta.data, _CountedData)
        assert meta.data.counted_seconds == 3

    def test_parameterized_meta_model_dump_is_plain_dict(self) -> None:
        meta = CeleryTaskMeta[_CountedData](data=_CountedData(counted_seconds=3))

        dumped = meta.model_dump()

        assert dumped['data'] == {'counted_seconds': 3}


class _HookedData(TaskDataModel):
    counted_seconds: int | None = None


class TaskDataModelTestCase(SimpleTestCase):
    @staticmethod
    def _make() -> tuple[_HookedData, list]:
        fires = []
        data = _HookedData()
        data._on_change = lambda: fires.append(1)
        return data, fires

    def test_change_hook_fires_on_every_attribute_set(self) -> None:
        data, fires = self._make()

        data.counted_seconds = 1
        data.counted_seconds = 2
        data.bananas = 'key'

        assert fires == [1, 1, 1]

    def test_assignment_is_validated(self) -> None:
        data, fires = self._make()

        with pytest.raises(ValidationError):
            data.counted_seconds = 'not-an-int'

        assert fires == []

    def test_extra_fields_are_allowed(self) -> None:
        data, fires = self._make()

        data.worker_hostname = 'host-1'

        assert data.model_dump() == {'counted_seconds': None, 'worker_hostname': 'host-1'}
        assert fires == [1]

    def test_no_hook_means_no_callback(self) -> None:
        data = _HookedData()

        data.counted_seconds = 5

        assert data.counted_seconds == 5


class CeleryTaskTrackerFinishTestCase(SimpleTestCase):
    def test_finish_success_marks_meta_completed(self) -> None:
        tracker = CeleryTaskTracker(_make_untracked_task())

        tracker.finish(states.SUCCESS)

        assert tracker.meta.progress == 1.0
        assert tracker.meta.completed_time is not None

    def test_finish_failure_marks_meta_failed(self) -> None:
        tracker = CeleryTaskTracker(_make_untracked_task())

        tracker.finish(states.FAILURE, exc=ValueError('boom'))

        assert tracker.meta.error == 'ValueError: boom'
        assert tracker.meta.failed_time is not None
        assert tracker.meta.completed_time is None

    def test_finish_failure_without_exc_leaves_meta_untouched(self) -> None:
        tracker = CeleryTaskTracker(_make_untracked_task())

        tracker.finish(states.FAILURE)

        assert tracker.meta.error is None
        assert tracker.meta.failed_time is None

    def test_finish_writes_final_meta_to_derived_key_not_main(self) -> None:
        task = _make_task()
        tracker = CeleryTaskTracker(task)

        tracker.finish(states.SUCCESS)

        args = task.backend.store_result.call_args.args
        assert args[0] == derive_final_meta_key('test-task-id')
        assert task.backend.store_result.call_count == 1

    def test_finish_final_meta_carries_last_mid_run_data(self) -> None:
        task = _make_task()
        tracker = CeleryTaskTracker(task)
        tracker.meta.data['counted_seconds'] = 10
        tracker.meta.data['more'] = {'has_noises': True}

        tracker.finish(states.SUCCESS)

        args = task.backend.store_result.call_args.args
        assert args[1]['data'] == {'counted_seconds': 10, 'more': {'has_noises': True}}
        assert args[1]['progress'] == 1.0
        assert args[1]['completed_time'] is not None
        assert args[2] == states.SUCCESS

    def test_finish_failure_final_meta_carries_error_on_success_row(self) -> None:
        task = _make_task()
        tracker = CeleryTaskTracker(task)

        tracker.finish(states.FAILURE, exc=ValueError('boom'))

        args = task.backend.store_result.call_args.args
        assert args[0] == derive_final_meta_key('test-task-id')
        assert args[1]['error'] == 'ValueError: boom'
        assert args[1]['failed_time'] is not None
        assert args[2] == states.SUCCESS

    def test_finish_untracked_does_not_push_final_meta(self) -> None:
        task = _make_untracked_task()
        tracker = CeleryTaskTracker(task)

        tracker.finish(states.SUCCESS)

        task.backend.store_result.assert_not_called()

    def test_finish_push_final_meta_swallows_backend_errors(self) -> None:
        task = _make_task()
        task.backend.store_result.side_effect = Exception('backend down')
        tracker = CeleryTaskTracker(task)

        tracker.finish(states.SUCCESS)


class CeleryTaskTrackerBackendSinkTestCase(SimpleTestCase):
    def test_build_snapshot_uses_current_state_and_meta(self) -> None:
        tracker = CeleryTaskTracker(_make_untracked_task())
        tracker.update_state('MAKING NOISES')
        tracker.meta.data['bananas'] = 'key'

        snapshot = tracker._build_snapshot()

        assert snapshot.state == 'MAKING NOISES'
        assert snapshot.meta_dict['data'] == {'bananas': 'key'}

    def test_push_to_backend_stores_meta_dict_and_state(self) -> None:
        task = _make_task()
        tracker = CeleryTaskTracker(task)
        tracker.meta.data['counted_seconds'] = 3

        tracker._push_to_backend(tracker._build_snapshot())

        args = task.backend.store_result.call_args.args
        assert args[0] == 'test-task-id'
        assert args[1]['data']['counted_seconds'] == 3
        assert args[2] == states.PENDING

    def test_push_to_backend_noop_without_request_id(self) -> None:
        task = _make_untracked_task()
        tracker = CeleryTaskTracker(task)

        tracker._push_to_backend(tracker._build_snapshot())

        task.backend.store_result.assert_not_called()

    def test_push_to_backend_swallows_backend_errors(self) -> None:
        task = _make_task()
        task.backend.store_result.side_effect = Exception('backend down')
        tracker = CeleryTaskTracker(task)

        tracker._push_to_backend(tracker._build_snapshot())


class CeleryTaskTrackerFlusherTestCase(SimpleTestCase):
    def setUp(self) -> None:
        patcher = patch.object(CeleryTaskTracker, '_FLUSH_TIMEOUT_SECONDS', 1)
        patcher.start()
        self.addCleanup(patcher.stop)

    def _make_tracked(self) -> CeleryTaskTracker:
        tracker = CeleryTaskTracker(_make_task())
        self.addCleanup(self._stop, tracker)
        return tracker

    @staticmethod
    def _stop(tracker: CeleryTaskTracker) -> None:
        tracker._stopped.set()
        tracker._pending_event.set()
        if tracker._flusher is not None:
            tracker._flusher.join(timeout=6)

    @staticmethod
    def _wait_until(condition: Callable[[], bool], timeout_seconds: float = 5) -> None:
        deadline = time.time() + timeout_seconds
        while not condition():
            if time.time() > deadline:
                message = 'Flusher test timed out'
                raise TimeoutError(message)
            time.sleep(0.01)

    def test_flushes_coalesce_to_latest_snapshot(self) -> None:
        tracker = self._make_tracked()
        store = tracker.task.backend.store_result
        tracker.update_state('MAKING NOISES')
        for i in range(100):
            tracker.meta.data['counted_seconds'] = i

        self._wait_until(lambda: store.call_count >= 1)
        self._wait_until(
            lambda: (
                store.call_count >= 1
                and store.call_args.args[1]['data'].get('counted_seconds') == 99
            )
        )

        assert store.call_count < 100
        last_args = store.call_args.args
        assert last_args[0] == 'test-task-id'
        assert last_args[2] == 'MAKING NOISES'
        assert last_args[1]['data']['counted_seconds'] == 99

    def test_flushes_apply_in_order(self) -> None:
        tracker = self._make_tracked()
        store = tracker.task.backend.store_result

        tracker.update_state('STATE ONE')
        self._wait_until(lambda: store.call_count >= 1)
        tracker.update_state('STATE TWO')
        self._wait_until(lambda: store.call_count >= 2)

        flushed_states = [call.args[2] for call in store.call_args_list[:2]]
        assert flushed_states == ['STATE ONE', 'STATE TWO']

    def test_flusher_uses_task_id_captured_at_construction(self) -> None:
        task = _make_task()
        tracker = CeleryTaskTracker(task)
        self.addCleanup(self._stop, tracker)
        store = tracker.task.backend.store_result

        task.request.id = None

        tracker.update_state('MAKING NOISES')

        self._wait_until(lambda: store.call_count >= 1)
        assert store.call_args.args[0] == 'test-task-id'

    def test_finish_stops_flusher_without_terminal_write(self) -> None:
        tracker = self._make_tracked()
        store = tracker.task.backend.store_result

        tracker.update_state('STATE ONE')
        self._wait_until(lambda: store.call_count >= 1)

        tracker.finish(states.SUCCESS)
        calls_after_finish = store.call_count

        assert tracker._stopped.is_set()
        self._wait_until(lambda: not tracker._flusher.is_alive(), timeout_seconds=6)
        assert store.call_count == calls_after_finish

    def test_stop_flusher_wakes_pending_wait(self) -> None:
        tracker = self._make_tracked()
        tracker._pending_event.clear()

        tracker._stop_flusher()

        assert tracker._pending_event.is_set()

    def test_join_timeout_logs_warning(self) -> None:
        tracker = self._make_tracked()
        store = tracker.task.backend.store_result

        def slow_store_result(*_args: Any) -> None:
            time.sleep(2)

        store.side_effect = slow_store_result
        tracker.update_state('STATE ONE')
        self._wait_until(lambda: store.call_count >= 1)
        tracker.update_state('STATE TWO')
        self._wait_until(lambda: store.call_count >= 2)

        with self.assertLogs('django_spire.celery.tracker', level='WARNING') as logs:
            tracker._stop_flusher()

        assert any('did not stop' in message for message in logs.output)
