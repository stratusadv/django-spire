from __future__ import annotations

import pickle
from unittest.mock import MagicMock, patch, PropertyMock

from celery import states
from django.test import TestCase
from django.utils.timezone import now
from sqlalchemy.exc import OperationalError

from django_spire.celery.models import CeleryTask
from django_spire.celery.services.service import CeleryTaskService
from django_spire.celery.tests.factories import create_test_celery_task

_TRACK_CONFIGURED = (
    'django_spire.metric.domain.statistic.services.tracking_service'
    '.StatisticTrackingService.track_configured'
)


def _backend_error() -> OperationalError:
    return OperationalError('SELECT 1', {}, Exception('backend down'))


def _mock_async_result(state: str, info: dict | None = None, **overrides) -> MagicMock:
    mock_result = MagicMock()
    mock_result.state = state
    mock_result.info = info
    mock_result.traceback = 'Traceback (most recent call last):\nValueError: task boom'
    for key, value in overrides.items():
        setattr(mock_result, key, value)

    return mock_result


class CeleryTaskServiceCaptureResultLazyTestCase(TestCase):
    def setUp(self) -> None:
        self.celery_task = create_test_celery_task(state=states.SUCCESS)
        self.service = CeleryTaskService(obj=self.celery_task)

    def test_captures_result_and_completed_datetime(self) -> None:
        completed_time = now()
        mock_result = _mock_async_result(
            states.SUCCESS, get=MagicMock(return_value='test result'), date_done=completed_time
        )

        self.service._capture_result_lazy(mock_result)

        assert self.celery_task.result == 'test result'
        assert self.celery_task.completed_datetime == completed_time

    def test_naive_date_done_is_made_aware(self) -> None:
        mock_result = _mock_async_result(
            states.SUCCESS,
            get=MagicMock(return_value='test result'),
            date_done=now().replace(tzinfo=None),
        )

        self.service._capture_result_lazy(mock_result)

        assert self.celery_task.completed_datetime.tzinfo is not None

    def test_backend_error_leaves_celery_task_unchanged(self) -> None:
        mock_result = _mock_async_result(
            states.SUCCESS, get=MagicMock(side_effect=_backend_error())
        )

        self.service._capture_result_lazy(mock_result)

        assert self.celery_task.has_no_result


class CeleryTaskServiceUpdateFromBackendTestCase(TestCase):
    def setUp(self) -> None:
        self.celery_task = create_test_celery_task(state=states.STARTED)
        self.service = CeleryTaskService(obj=self.celery_task)

    @patch.object(CeleryTask, 'async_result', new_callable=PropertyMock)
    def test_pending_to_started_merges_meta(self, mock_async_result: MagicMock) -> None:
        self.celery_task.state = states.PENDING
        self.celery_task.save()

        mock_async_result.return_value = _mock_async_result(
            states.STARTED, info={'progress': 0.4, 'data': {'counted_seconds': 3}}
        )

        self.service.update_from_backend()

        assert self.celery_task.state == states.STARTED
        assert self.celery_task.meta.progress == 0.4
        assert self.celery_task.meta.data == {'counted_seconds': 3}

    @patch(_TRACK_CONFIGURED)
    @patch.object(CeleryTask, 'async_result', new_callable=PropertyMock)
    def test_started_to_success_captures_result_and_records_metric(
        self, mock_async_result: MagicMock, mock_track_configured: MagicMock
    ) -> None:
        mock_async_result.return_value = _mock_async_result(
            states.SUCCESS, get=MagicMock(return_value='The pirate says YARR')
        )

        self.service.update_from_backend()

        assert self.celery_task.state == states.SUCCESS
        assert self.celery_task.result == 'The pirate says YARR'
        assert self.celery_task.completed_datetime is not None
        assert self.celery_task.meta.progress == 1.0
        assert self.celery_task.meta.completed_time is not None
        mock_track_configured.assert_called_once_with(reference='celery_task_success')

    @patch(_TRACK_CONFIGURED)
    @patch.object(CeleryTask, 'async_result', new_callable=PropertyMock)
    def test_started_to_failure_stores_exception_result_and_records_metric(
        self, mock_async_result: MagicMock, mock_track_configured: MagicMock
    ) -> None:
        mock_async_result.return_value = _mock_async_result(
            states.FAILURE, get=MagicMock(side_effect=ValueError('task boom'))
        )

        self.service.update_from_backend()

        assert self.celery_task.state == states.FAILURE
        assert self.celery_task.has_exception_result

        exception_result = self.celery_task.exception_result
        assert exception_result is not None
        assert exception_result.exc_type == 'ValueError'
        assert exception_result.message == 'task boom'

        assert self.celery_task.meta.error == 'task boom'
        assert self.celery_task.meta.completed_time is None
        assert self.celery_task.completed_datetime is not None
        mock_track_configured.assert_called_once_with(reference='celery_task_failure')

    @patch(_TRACK_CONFIGURED)
    @patch.object(CeleryTask, 'async_result', new_callable=PropertyMock)
    def test_started_to_retry_records_metric(
        self, mock_async_result: MagicMock, mock_track_configured: MagicMock
    ) -> None:
        mock_async_result.return_value = _mock_async_result(states.RETRY, info={'retries': 1})

        self.service.update_from_backend()

        assert self.celery_task.state == states.RETRY
        assert self.celery_task.meta.retries == 1
        mock_track_configured.assert_called_once_with(reference='celery_task_retry')

    @patch(_TRACK_CONFIGURED)
    @patch.object(CeleryTask, 'async_result', new_callable=PropertyMock)
    def test_success_with_unavailable_backend_result(
        self, mock_async_result: MagicMock, mock_track_configured: MagicMock
    ) -> None:
        mock_async_result.return_value = _mock_async_result(
            states.SUCCESS, get=MagicMock(side_effect=_backend_error())
        )

        self.service.update_from_backend()

        assert self.celery_task.state == states.SUCCESS
        assert self.celery_task.has_no_result
        mock_track_configured.assert_called_once_with(reference='celery_task_success')

    @patch.object(CeleryTask, 'async_result', new_callable=PropertyMock)
    def test_ready_celery_task_with_missing_result_retries_capture(
        self, mock_async_result: MagicMock
    ) -> None:
        self.celery_task.state = states.SUCCESS
        self.celery_task.save()

        completed_time = now()
        mock_async_result.return_value = _mock_async_result(
            states.SUCCESS, get=MagicMock(return_value='late result'), date_done=completed_time
        )

        self.service.update_from_backend()

        assert self.celery_task.result == 'late result'
        assert self.celery_task.completed_datetime == completed_time

    @patch(_TRACK_CONFIGURED)
    @patch.object(CeleryTask, 'async_result', new_callable=PropertyMock)
    def test_terminal_celery_task_ignores_stale_backend_state(
        self, mock_async_result: MagicMock, mock_track_configured: MagicMock
    ) -> None:
        self.celery_task.state = states.SUCCESS
        self.celery_task._result = pickle.dumps('done')
        self.celery_task.save()

        mock_async_result.return_value = _mock_async_result(states.STARTED, info={'progress': 0.2})

        self.service.update_from_backend()

        assert self.celery_task.state == states.SUCCESS
        assert self.celery_task.result == 'done'
        mock_track_configured.assert_not_called()


class ApplyBackendSnapshotTestCase(TestCase):
    def test_stale_transition_after_terminal_is_dropped(self) -> None:
        celery_task = create_test_celery_task(state=states.SUCCESS)

        records_metric = celery_task.services._apply_backend_snapshot(
            states.STARTED, meta_dict={'progress': 0.2}
        )

        assert records_metric is False
        celery_task.refresh_from_db()
        assert celery_task.state == states.SUCCESS

    def test_no_regression_to_pending(self) -> None:
        celery_task = create_test_celery_task(state=states.STARTED)

        celery_task.services._apply_backend_snapshot(states.PENDING)

        celery_task.refresh_from_db()
        assert celery_task.state == states.STARTED

    def test_monotonic_progress_never_decreases(self) -> None:
        celery_task = create_test_celery_task(state=states.STARTED)
        celery_task.meta_as_dict = {'progress': 0.5}
        celery_task.save()

        celery_task.services._apply_backend_snapshot(states.STARTED, meta_dict={'progress': 0.2})

        celery_task.refresh_from_db()
        assert celery_task.meta.progress == 0.5

    def test_unchanged_snapshot_is_a_noop(self) -> None:
        celery_task = create_test_celery_task(state=states.STARTED)
        celery_task.meta = celery_task.meta
        celery_task.save()

        with patch.object(CeleryTask, 'save') as mock_save:
            records_metric = celery_task.services._apply_backend_snapshot(
                states.STARTED, meta_dict={}
            )

        assert records_metric is False
        mock_save.assert_not_called()

    def test_started_to_success_sets_result_and_completed_datetime(self) -> None:
        celery_task = create_test_celery_task(state=states.STARTED)

        records_metric = celery_task.services._apply_backend_snapshot(
            states.SUCCESS, result='the result'
        )

        assert records_metric is True
        celery_task.refresh_from_db()
        assert celery_task.state == states.SUCCESS
        assert celery_task.result == 'the result'
        assert celery_task.completed_datetime is not None
