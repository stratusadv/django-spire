from __future__ import annotations

from concurrent.futures import Future
from typing import Any, Callable
from unittest.mock import MagicMock, patch

import pytest
from django.test import SimpleTestCase

from django_spire.celery.meta import CeleryTaskMeta
from django_spire.celery.tracker import CeleryTaskTracker


def _completed_future(fn: Callable[..., Any], *args: Any, **kwargs: Any) -> Future:
    future = Future()
    try:
        future.set_result(fn(*args, **kwargs))
    except Exception as e:
        future.set_exception(e)
    return future


def _make_task() -> MagicMock:
    task = MagicMock()
    task.request.id = 'test-task-id'
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


class CeleryTaskTrackerStatePushTestCase(SimpleTestCase):
    def test_state_updates_are_pushed_to_backend_with_meta_dict(self) -> None:
        task = _make_task()

        with (
            patch('django_spire.celery.tracker._async_update_state') as mock_update_state,
            patch(
                'django_spire.celery.tracker._state_update_executor.submit',
                side_effect=_completed_future,
            ),
        ):
            tracker = CeleryTaskTracker(task)
            tracker.update_state('MAKING NOISES')

            mock_update_state.assert_called_once()
            args = mock_update_state.call_args
            assert args.kwargs == {}
            assert args.args[0] is task.backend
            assert args.args[1] == 'test-task-id'
            assert args.args[2] == 'MAKING NOISES'
            assert isinstance(args.args[3], dict)

    def test_set_completed_after_progress_does_not_raise(self) -> None:
        task = _make_task()

        with patch(
            'django_spire.celery.tracker._state_update_executor.submit',
            side_effect=_completed_future,
        ):
            tracker = CeleryTaskTracker(task)
            tracker.set_started()
            tracker.update_count_progress(5, 10)
            tracker.update_state('MAKING NOISES')
            tracker.set_completed()

    def test_update_state_uppercases_state(self) -> None:
        task = _make_task()

        with patch(
            'django_spire.celery.tracker._state_update_executor.submit',
            side_effect=_completed_future,
        ):
            tracker = CeleryTaskTracker(task)
            tracker.update_state('making noises')
            assert tracker._state == 'MAKING NOISES'

    def test_set_completed_marks_meta_completed(self) -> None:
        task = _make_task()

        with patch(
            'django_spire.celery.tracker._state_update_executor.submit',
            side_effect=_completed_future,
        ):
            tracker = CeleryTaskTracker(task)
            tracker.set_completed()

        assert tracker.meta.progress == 1.0
        assert tracker.meta.completed_time is not None


class CeleryTaskTrackerProgressTestCase(SimpleTestCase):
    def test_update_count_progress_sets_progress(self) -> None:
        task = _make_task()
        tracker = CeleryTaskTracker(task)
        tracker.meta.last_update_time = 0
        tracker.meta.set_started()

        tracker.update_count_progress(5, 10)

        assert tracker.meta.progress == 0.5

    def test_update_count_progress_validates_range(self) -> None:
        task = _make_task()
        tracker = CeleryTaskTracker(task)

        with pytest.raises(ValueError, match='Progress range is invalid'):
            tracker.update_count_progress(1, 10, range_min=2.0, range_max=1.0)

    def test_update_cumulative_progress_without_target_raises(self) -> None:
        task = _make_task()
        tracker = CeleryTaskTracker(task)

        with pytest.raises(ValueError, match='Cumulative Progress Target Value'):
            tracker.update_cumulative_progress(1)

    def test_update_cumulative_progress_sets_progress(self) -> None:
        task = _make_task()
        tracker = CeleryTaskTracker(task)
        tracker.meta.last_update_time = 0
        tracker.meta.set_started()
        tracker.set_cumulative_progress_target_value(10)

        tracker.update_cumulative_progress(3)

        assert tracker.meta.progress == 0.3


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

    def test_model_dump_excludes_progress_updates_count(self) -> None:
        meta = CeleryTaskMeta()
        dumped = meta.model_dump()

        assert '_progress_updates_count' not in dumped
        assert dumped['data'] == {}
        assert dumped['progress'] is None

    def test_default_data_field_is_isolated_per_instance(self) -> None:
        first = CeleryTaskMeta()
        second = CeleryTaskMeta()
        first.data['key'] = 'value'

        assert second.data == {}
