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


def _mock_async_result(state: str, info: dict | str | None = None, **overrides) -> MagicMock:
    mock_result = MagicMock()
    mock_result._get_task_meta.return_value = {'status': state, 'result': info}
    mock_result.backend.get_task_meta.return_value = {'status': states.PENDING, 'result': None}
    mock_result.traceback = 'Traceback (most recent call last):\nValueError: task boom'
    for key, value in overrides.items():
        setattr(mock_result, key, value)

    return mock_result


def _set_final_meta(mock_result: MagicMock, final_meta: dict | None) -> None:
    mock_result.backend.get_task_meta.return_value = {
        'status': states.SUCCESS,
        'result': final_meta,
    }


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

    @patch.object(CeleryTask, 'async_result', new_callable=PropertyMock)
    def test_non_dict_meta_for_unready_state_is_dropped_without_error(
        self, mock_async_result: MagicMock
    ) -> None:
        mock_async_result.return_value = _mock_async_result(
            states.STARTED, info='The sword goes SWOOSH SWOOSH SWOOSH SWOOSH SWOOSH'
        )

        self.service.update_from_backend()

        self.celery_task.refresh_from_db()
        assert self.celery_task.state == states.STARTED

    @patch.object(CeleryTask, 'async_result', new_callable=PropertyMock)
    def test_native_tracker_started_row_meta_is_dropped(self, mock_async_result: MagicMock) -> None:
        self.celery_task.state = states.PENDING
        self.celery_task.save()

        mock_async_result.return_value = _mock_async_result(
            states.STARTED, info={'pid': 249397, 'hostname': 'celery@not-a-toaster'}
        )

        self.service.update_from_backend()

        self.celery_task.refresh_from_db()
        assert self.celery_task.state == states.STARTED
        assert self.celery_task.meta.data == {}
        assert self.celery_task.meta.progress is None
        assert 'pid' not in self.celery_task.meta.model_dump()
        assert 'hostname' not in self.celery_task.meta.model_dump()


class CeleryTaskServiceFinalMetaTestCase(TestCase):
    def setUp(self) -> None:
        self.celery_task = create_test_celery_task(state=states.STARTED)
        self.service = CeleryTaskService(obj=self.celery_task)

    @patch(_TRACK_CONFIGURED)
    @patch.object(CeleryTask, 'async_result', new_callable=PropertyMock)
    def test_success_terminal_merges_final_meta_over_stale_web_meta(
        self, mock_async_result: MagicMock, mock_track_configured: MagicMock
    ) -> None:
        self.celery_task.meta_as_dict = {'progress': 0.7, 'data': {'counted_seconds': 7}}
        self.celery_task.save()

        mock_result = _mock_async_result(
            states.SUCCESS, get=MagicMock(return_value='The pirate says YARR')
        )
        _set_final_meta(
            mock_result,
            {
                'data': {'counted_seconds': 10, 'more': {'has_noises': True}},
                'progress': 1.0,
                'completed_time': 123.0,
                'started_time': 100.0,
                'last_update_time': 122.0,
                'retries': 0,
            },
        )
        mock_async_result.return_value = mock_result

        self.service.update_from_backend()

        assert self.celery_task.state == states.SUCCESS
        assert self.celery_task.meta.data == {'counted_seconds': 10, 'more': {'has_noises': True}}
        assert self.celery_task.meta.completed_time == 123.0
        assert self.celery_task.result == 'The pirate says YARR'
        mock_track_configured.assert_called_once_with(reference='celery_task_success')

    @patch(_TRACK_CONFIGURED)
    @patch.object(CeleryTask, 'async_result', new_callable=PropertyMock)
    def test_failure_terminal_merges_final_meta_error_and_data(
        self, mock_async_result: MagicMock, mock_track_configured: MagicMock
    ) -> None:
        self.celery_task.meta_as_dict = {'progress': 0.4, 'data': {'counted_seconds': 3}}
        self.celery_task.save()

        mock_result = _mock_async_result(
            states.FAILURE, get=MagicMock(side_effect=ValueError('task boom'))
        )
        _set_final_meta(
            mock_result,
            {
                'data': {'counted_seconds': 4},
                'progress': 0.4,
                'error': 'ValueError: task boom',
                'failed_time': 55.0,
                'retries': 0,
            },
        )
        mock_async_result.return_value = mock_result

        self.service.update_from_backend()

        assert self.celery_task.state == states.FAILURE
        assert self.celery_task.meta.data == {'counted_seconds': 4}
        assert self.celery_task.meta.error == 'ValueError: task boom'
        assert self.celery_task.meta.failed_time == 55.0
        assert self.celery_task.has_exception_result
        exception_result = self.celery_task.exception_result
        assert exception_result is not None
        assert exception_result.exc_type == 'ValueError'
        assert exception_result.message == 'task boom'
        mock_track_configured.assert_called_once_with(reference='celery_task_failure')

    @patch(_TRACK_CONFIGURED)
    @patch.object(CeleryTask, 'async_result', new_callable=PropertyMock)
    def test_retry_terminal_merges_final_meta_retries(
        self, mock_async_result: MagicMock, mock_track_configured: MagicMock
    ) -> None:
        mock_result = _mock_async_result(states.RETRY, info=None)
        _set_final_meta(
            mock_result, {'retries': 2, 'data': {'counted_seconds': 4}, 'progress': 0.4}
        )
        mock_async_result.return_value = mock_result

        self.service.update_from_backend()

        assert self.celery_task.state == states.RETRY
        assert self.celery_task.meta.retries == 2
        assert self.celery_task.meta.data == {'counted_seconds': 4}
        mock_track_configured.assert_called_once_with(reference='celery_task_retry')

    @patch(_TRACK_CONFIGURED)
    @patch.object(CeleryTask, 'async_result', new_callable=PropertyMock)
    def test_success_terminal_without_final_meta_row_keeps_web_meta(
        self, mock_async_result: MagicMock, mock_track_configured: MagicMock
    ) -> None:
        self.celery_task.meta_as_dict = {'progress': 0.7, 'data': {'counted_seconds': 7}}
        self.celery_task.save()

        mock_result = _mock_async_result(
            states.SUCCESS, get=MagicMock(return_value='The pirate says YARR')
        )
        mock_async_result.return_value = mock_result

        self.service.update_from_backend()

        assert self.celery_task.state == states.SUCCESS
        assert self.celery_task.meta.data == {'counted_seconds': 7}
        assert self.celery_task.meta.progress == 1.0
        assert self.celery_task.meta.completed_time is not None
        mock_track_configured.assert_called_once_with(reference='celery_task_success')

    @patch(_TRACK_CONFIGURED)
    @patch.object(CeleryTask, 'async_result', new_callable=PropertyMock)
    def test_success_terminal_final_meta_read_error_still_transitions(
        self, mock_async_result: MagicMock, mock_track_configured: MagicMock
    ) -> None:
        mock_result = _mock_async_result(
            states.SUCCESS, get=MagicMock(return_value='The pirate says YARR')
        )
        mock_result.backend.get_task_meta.side_effect = _backend_error()
        mock_async_result.return_value = mock_result

        self.service.update_from_backend()

        assert self.celery_task.state == states.SUCCESS
        assert self.celery_task.result == 'The pirate says YARR'
        mock_track_configured.assert_called_once_with(reference='celery_task_success')

    @patch(_TRACK_CONFIGURED)
    @patch.object(CeleryTask, 'async_result', new_callable=PropertyMock)
    def test_success_terminal_non_dict_final_meta_is_dropped(
        self, mock_async_result: MagicMock, mock_track_configured: MagicMock
    ) -> None:
        mock_result = _mock_async_result(
            states.SUCCESS, get=MagicMock(return_value='The pirate says YARR')
        )
        mock_result.backend.get_task_meta.return_value = {
            'status': states.SUCCESS,
            'result': 'not-meta',
        }
        mock_async_result.return_value = mock_result

        self.service.update_from_backend()

        assert self.celery_task.state == states.SUCCESS
        assert self.celery_task.meta.data == {}
        mock_track_configured.assert_called_once_with(reference='celery_task_success')


class CeleryTaskServiceStuckRowHealTestCase(TestCase):
    def setUp(self) -> None:
        self.celery_task = create_test_celery_task(state=states.STARTED)
        self.service = CeleryTaskService(obj=self.celery_task)

    @patch(_TRACK_CONFIGURED)
    @patch.object(CeleryTask, 'async_result', new_callable=PropertyMock)
    def test_stuck_started_with_final_meta_completed_time_heals_to_success(
        self, mock_async_result: MagicMock, mock_track_configured: MagicMock
    ) -> None:
        self.celery_task.meta_as_dict = {'progress': 0.5, 'data': {'counted_seconds': 5}}
        self.celery_task.save()

        mock_result = _mock_async_result(
            states.STARTED, info={'progress': 0.5, 'data': {'counted_seconds': 5}}
        )
        _set_final_meta(
            mock_result,
            {
                'data': {'counted_seconds': 10, 'more': {'has_noises': True}},
                'progress': 1.0,
                'completed_time': 123.0,
                'started_time': 100.0,
                'retries': 0,
            },
        )
        mock_async_result.return_value = mock_result

        self.service.update_from_backend()

        assert self.celery_task.state == states.SUCCESS
        assert self.celery_task.meta.data == {'counted_seconds': 10, 'more': {'has_noises': True}}
        assert self.celery_task.meta.completed_time == 123.0
        assert self.celery_task.completed_datetime is not None
        assert self.celery_task.has_no_result
        mock_track_configured.assert_called_once_with(reference='celery_task_success')

    @patch(_TRACK_CONFIGURED)
    @patch.object(CeleryTask, 'async_result', new_callable=PropertyMock)
    def test_stuck_started_with_final_meta_error_heals_to_failure(
        self, mock_async_result: MagicMock, mock_track_configured: MagicMock
    ) -> None:
        self.celery_task.meta_as_dict = {'progress': 0.4, 'data': {'counted_seconds': 3}}
        self.celery_task.save()

        mock_result = _mock_async_result(
            states.STARTED, info={'progress': 0.4, 'data': {'counted_seconds': 3}}
        )
        _set_final_meta(
            mock_result,
            {
                'data': {'counted_seconds': 4},
                'progress': 0.4,
                'error': 'ValueError: task boom',
                'failed_time': 55.0,
                'retries': 0,
            },
        )
        mock_async_result.return_value = mock_result

        self.service.update_from_backend()

        assert self.celery_task.state == states.FAILURE
        assert self.celery_task.meta.error == 'ValueError: task boom'
        assert self.celery_task.meta.failed_time == 55.0
        assert self.celery_task.meta.data == {'counted_seconds': 4}
        assert self.celery_task.has_exception_result
        exception_result = self.celery_task.exception_result
        assert exception_result is not None
        assert exception_result.message == 'ValueError: task boom'
        mock_track_configured.assert_called_once_with(reference='celery_task_failure')

    @patch(_TRACK_CONFIGURED)
    @patch.object(CeleryTask, 'async_result', new_callable=PropertyMock)
    def test_stuck_started_with_final_meta_neither_heals_to_retry(
        self, mock_async_result: MagicMock, mock_track_configured: MagicMock
    ) -> None:
        mock_result = _mock_async_result(
            states.STARTED, info={'progress': 0.2, 'data': {'counted_seconds': 1}}
        )
        _set_final_meta(
            mock_result, {'retries': 2, 'data': {'counted_seconds': 4}, 'progress': 0.4}
        )
        mock_async_result.return_value = mock_result

        self.service.update_from_backend()

        assert self.celery_task.state == states.RETRY
        assert self.celery_task.meta.retries == 2
        assert self.celery_task.meta.data == {'counted_seconds': 4}
        assert self.celery_task.completed_datetime is None
        mock_track_configured.assert_called_once_with(reference='celery_task_retry')

    @patch(_TRACK_CONFIGURED)
    @patch.object(CeleryTask, 'async_result', new_callable=PropertyMock)
    def test_stuck_custom_state_with_final_meta_heals_to_success(
        self, mock_async_result: MagicMock, mock_track_configured: MagicMock
    ) -> None:
        self.celery_task.state = 'MAKING NOISES'
        self.celery_task.save()

        mock_result = _mock_async_result(
            'MAKING NOISES', info={'progress': 0.6, 'data': {'counted_seconds': 6}}
        )
        _set_final_meta(
            mock_result,
            {
                'data': {'counted_seconds': 8},
                'progress': 1.0,
                'completed_time': 123.0,
                'retries': 0,
            },
        )
        mock_async_result.return_value = mock_result

        self.service.update_from_backend()

        assert self.celery_task.state == states.SUCCESS
        assert self.celery_task.meta.data == {'counted_seconds': 8}
        mock_track_configured.assert_called_once_with(reference='celery_task_success')

    @patch(_TRACK_CONFIGURED)
    @patch.object(CeleryTask, 'async_result', new_callable=PropertyMock)
    def test_stuck_started_without_final_meta_row_is_unchanged(
        self, mock_async_result: MagicMock, mock_track_configured: MagicMock
    ) -> None:
        mock_async_result.return_value = _mock_async_result(
            states.STARTED, info={'progress': 0.5, 'data': {'counted_seconds': 5}}
        )

        self.service.update_from_backend()

        assert self.celery_task.state == states.STARTED
        assert self.celery_task.meta.data == {'counted_seconds': 5}
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
