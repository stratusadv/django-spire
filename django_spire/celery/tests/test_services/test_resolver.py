from __future__ import annotations

from datetime import timedelta
from typing import Any
from unittest.mock import MagicMock, patch

from celery import states
from django.test import TestCase
from django.utils.timezone import now
from sqlalchemy.exc import OperationalError

from django_spire.celery.models import CeleryTask
from django_spire.celery.services.resolver import resolve_celery_tasks
from django_spire.celery.tests.factories import create_test_celery_task

_TRACK_CONFIGURED = (
    'django_spire.metric.domain.statistic.services.tracking_service'
    '.StatisticTrackingService.track_configured'
)


def _mock_async_result(state: str, info: dict | str | None = None, **overrides) -> MagicMock:
    mock_result = MagicMock()
    mock_result._get_task_meta.return_value = {'status': state, 'result': info}
    mock_result.backend.get_task_meta.return_value = {'status': states.PENDING, 'result': None}
    mock_result.traceback = 'Traceback (most recent call last):\nValueError: task boom'
    for key, value in overrides.items():
        setattr(mock_result, key, value)

    return mock_result


def _patch_async_results(tasks_by_pk: dict[int, MagicMock]) -> tuple[Any, MagicMock]:
    calls = MagicMock()

    def getter(celery_task: CeleryTask) -> MagicMock:
        calls(celery_task)
        return tasks_by_pk[celery_task.pk]

    patcher = patch.object(CeleryTask, 'async_result', new=property(getter))
    return patcher, calls


class ResolveCeleryTasksTestCase(TestCase):
    def test_resolves_unready_tasks_to_backend_terminal(self) -> None:
        task_a = create_test_celery_task(state=states.STARTED)
        task_b = create_test_celery_task(state=states.PENDING)

        patcher, _ = _patch_async_results(
            {
                task_a.pk: _mock_async_result(states.SUCCESS, get=MagicMock(return_value='done-a')),
                task_b.pk: _mock_async_result(states.SUCCESS, get=MagicMock(return_value='done-b')),
            }
        )

        with patcher:
            changed = resolve_celery_tasks(CeleryTask.objects.all())

        assert changed == 2
        task_a.refresh_from_db()
        task_b.refresh_from_db()
        assert task_a.state == states.SUCCESS
        assert task_a.result == 'done-a'
        assert task_b.state == states.SUCCESS
        assert task_b.result == 'done-b'

    @patch(_TRACK_CONFIGURED)
    def test_terminal_metric_fires_exactly_once_per_task(
        self, mock_track_configured: MagicMock
    ) -> None:
        task_a = create_test_celery_task(state=states.STARTED)
        task_b = create_test_celery_task(state=states.STARTED)

        patcher, _ = _patch_async_results(
            {
                task_a.pk: _mock_async_result(states.SUCCESS, get=MagicMock(return_value='a')),
                task_b.pk: _mock_async_result(
                    states.FAILURE, get=MagicMock(side_effect=ValueError('task boom'))
                ),
            }
        )

        with patcher:
            resolve_celery_tasks(CeleryTask.objects.all())

        references = [call.kwargs['reference'] for call in mock_track_configured.call_args_list]
        assert sorted(references) == ['celery_task_failure', 'celery_task_success']

    def test_stored_terminal_rows_are_left_untouched(self) -> None:
        done_task = create_test_celery_task(state=states.SUCCESS)
        running_task = create_test_celery_task(state=states.STARTED)

        patcher, calls = _patch_async_results(
            {
                running_task.pk: _mock_async_result(
                    states.SUCCESS, get=MagicMock(return_value='done')
                )
            }
        )

        with patcher:
            changed = resolve_celery_tasks(CeleryTask.objects.all())

        assert changed == 1
        done_task.refresh_from_db()
        assert done_task.state == states.SUCCESS
        assert calls.call_count == 1

    def test_limit_caps_attempts_in_queued_order(self) -> None:
        queued_time = now()
        first = create_test_celery_task(state=states.STARTED, queued_datetime=queued_time)
        second = create_test_celery_task(
            state=states.STARTED, queued_datetime=queued_time + timedelta(seconds=1)
        )
        third = create_test_celery_task(
            state=states.STARTED, queued_datetime=queued_time + timedelta(seconds=2)
        )

        patcher, _ = _patch_async_results(
            {
                first.pk: _mock_async_result(states.SUCCESS, get=MagicMock(return_value='1')),
                second.pk: _mock_async_result(states.SUCCESS, get=MagicMock(return_value='2')),
                third.pk: _mock_async_result(states.SUCCESS, get=MagicMock(return_value='3')),
            }
        )

        with patcher:
            changed = resolve_celery_tasks(CeleryTask.objects.all(), limit=2)

        assert changed == 2
        first.refresh_from_db()
        second.refresh_from_db()
        third.refresh_from_db()
        assert first.state == states.SUCCESS
        assert second.state == states.SUCCESS
        assert third.state == states.STARTED

    def test_per_task_backend_error_does_not_stop_the_loop(self) -> None:
        failing_task = create_test_celery_task(state=states.STARTED)
        healthy_task = create_test_celery_task(state=states.STARTED)

        failing_result = MagicMock()
        failing_result._get_task_meta = MagicMock(
            side_effect=OperationalError('SELECT 1', {}, Exception('backend down'))
        )

        patcher, _ = _patch_async_results(
            {
                failing_task.pk: failing_result,
                healthy_task.pk: _mock_async_result(
                    states.SUCCESS, get=MagicMock(return_value='done')
                ),
            }
        )

        with patcher:
            changed = resolve_celery_tasks(CeleryTask.objects.all())

        assert changed == 1
        failing_task.refresh_from_db()
        healthy_task.refresh_from_db()
        assert failing_task.state == states.STARTED
        assert healthy_task.state == states.SUCCESS

    def test_empty_queryset_returns_zero(self) -> None:
        patcher, calls = _patch_async_results({})

        with patcher:
            assert resolve_celery_tasks(CeleryTask.objects.none()) == 0

        calls.assert_not_called()
