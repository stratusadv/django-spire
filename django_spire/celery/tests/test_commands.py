from __future__ import annotations

import time
from io import StringIO
from types import SimpleNamespace
from typing import TYPE_CHECKING
from unittest.mock import MagicMock, PropertyMock, patch

from celery import states
from django.core.management import call_command
from django.test import TestCase

from django_spire.celery.tests.factories import create_test_celery_task

if TYPE_CHECKING:
    from django_spire.celery.models import CeleryTask

_COMMAND_MODULE = 'django_spire.celery.management.commands.prune_stale_started_celery_tasks'


def _with_last_update(celery_task: CeleryTask, last_update_time: float | None) -> CeleryTask:
    celery_task._task_meta = {**celery_task.meta.model_dump(), 'last_update_time': last_update_time}
    celery_task.save()
    return celery_task


class _BackendDownResult:
    @property
    def state(self) -> str:
        message = 'backend unavailable'
        raise RuntimeError(message)


def _fake_active_inspect(mock_app: MagicMock, active_by_worker: dict) -> None:
    mock_app.control.inspect.return_value.active.return_value = active_by_worker


class PruneStaleStartedCeleryTasksCommandTestCase(TestCase):
    @patch(f'{_COMMAND_MODULE}.current_app')
    @patch('django_spire.celery.models.CeleryTask.async_result', new_callable=PropertyMock)
    def test_stale_celery_task_is_marked_failure(
        self, mock_async_result: PropertyMock, mock_app: MagicMock
    ) -> None:
        celery_task = _with_last_update(
            create_test_celery_task(state=states.STARTED), time.time() - 700
        )
        mock_async_result.return_value = SimpleNamespace(state=states.STARTED)
        _fake_active_inspect(mock_app, {})

        call_command('prune_stale_started_celery_tasks')

        celery_task.refresh_from_db()
        assert celery_task.state == states.FAILURE
        assert celery_task.completed_datetime is not None
        assert celery_task.exception_result is not None
        assert celery_task.exception_result.exc_type == 'StaleStartedError'
        assert 'worker presumed dead' in celery_task.exception_result.message

    def test_fresh_celery_task_is_skipped(self) -> None:
        celery_task = _with_last_update(
            create_test_celery_task(state=states.STARTED), time.time() - 10
        )

        call_command('prune_stale_started_celery_tasks')

        celery_task.refresh_from_db()
        assert celery_task.state == states.STARTED
        assert celery_task.completed_datetime is None

    @patch(f'{_COMMAND_MODULE}.current_app')
    @patch('django_spire.celery.models.CeleryTask.async_result', new_callable=PropertyMock)
    def test_missing_last_update_time_is_stale(
        self, mock_async_result: PropertyMock, mock_app: MagicMock
    ) -> None:
        celery_task = create_test_celery_task(state=states.STARTED)
        mock_async_result.return_value = SimpleNamespace(state=states.STARTED)
        _fake_active_inspect(mock_app, {})

        call_command('prune_stale_started_celery_tasks')

        celery_task.refresh_from_db()
        assert celery_task.state == states.FAILURE

    def test_non_started_celery_tasks_are_untouched(self) -> None:
        success_celery_task = _with_last_update(
            create_test_celery_task(state=states.SUCCESS), time.time() - 700
        )
        pending_celery_task = _with_last_update(
            create_test_celery_task(state=states.PENDING), time.time() - 700
        )

        call_command('prune_stale_started_celery_tasks')

        success_celery_task.refresh_from_db()
        pending_celery_task.refresh_from_db()
        assert success_celery_task.state == states.SUCCESS
        assert pending_celery_task.state == states.PENDING

    @patch(f'{_COMMAND_MODULE}.current_app')
    @patch('django_spire.celery.models.CeleryTask.async_result', new_callable=PropertyMock)
    def test_threshold_option_changes_staleness(
        self, mock_async_result: PropertyMock, mock_app: MagicMock
    ) -> None:
        four_minutes_old = _with_last_update(
            create_test_celery_task(state=states.STARTED), time.time() - 240
        )
        fifteen_minutes_old = _with_last_update(
            create_test_celery_task(state=states.STARTED), time.time() - 900
        )
        mock_async_result.return_value = SimpleNamespace(state=states.STARTED)
        _fake_active_inspect(mock_app, {})

        call_command('prune_stale_started_celery_tasks', threshold=300)

        four_minutes_old.refresh_from_db()
        fifteen_minutes_old.refresh_from_db()
        assert four_minutes_old.state == states.STARTED
        assert fifteen_minutes_old.state == states.FAILURE

    @patch(f'{_COMMAND_MODULE}.current_app')
    @patch('django_spire.celery.models.CeleryTask.async_result', new_callable=PropertyMock)
    def test_dry_run_reports_without_updating(
        self, mock_async_result: PropertyMock, mock_app: MagicMock
    ) -> None:
        celery_task = _with_last_update(
            create_test_celery_task(state=states.STARTED), time.time() - 700
        )
        mock_async_result.return_value = SimpleNamespace(state=states.STARTED)
        _fake_active_inspect(mock_app, {})
        out = StringIO()

        call_command('prune_stale_started_celery_tasks', dry_run=True, stdout=out)

        celery_task.refresh_from_db()
        assert celery_task.state == states.STARTED
        assert '0 stale CeleryTask(s) would be synced from the backend.' in out.getvalue()
        assert '0 stale CeleryTask(s) would be skipped (task still alive).' in out.getvalue()
        assert '1 stale CeleryTask(s) would be marked FAILURE.' in out.getvalue()

    @patch('django_spire.celery.services.service.CeleryTaskService.update_from_backend')
    @patch('django_spire.celery.models.CeleryTask.async_result', new_callable=PropertyMock)
    def test_backend_terminal_syncs_instead_of_failure(
        self, mock_async_result: PropertyMock, mock_update: MagicMock
    ) -> None:
        celery_task = _with_last_update(
            create_test_celery_task(state=states.STARTED), time.time() - 700
        )
        mock_async_result.return_value = SimpleNamespace(state=states.SUCCESS)
        out = StringIO()

        call_command('prune_stale_started_celery_tasks', stdout=out)

        mock_update.assert_called_once()
        celery_task.refresh_from_db()
        assert celery_task.state == states.STARTED
        assert 'Synced 1 stale CeleryTask(s) from the backend.' in out.getvalue()

    @patch(f'{_COMMAND_MODULE}.current_app')
    @patch('django_spire.celery.models.CeleryTask.async_result', new_callable=PropertyMock)
    def test_active_on_worker_is_skipped(
        self, mock_async_result: PropertyMock, mock_app: MagicMock
    ) -> None:
        celery_task = _with_last_update(
            create_test_celery_task(state=states.STARTED), time.time() - 700
        )
        mock_async_result.return_value = SimpleNamespace(state=states.STARTED)
        _fake_active_inspect(
            mock_app, {'worker-1': [{'id': str(celery_task.task_id), 'name': 'song'}]}
        )

        call_command('prune_stale_started_celery_tasks')

        celery_task.refresh_from_db()
        assert celery_task.state == states.STARTED
        assert celery_task.completed_datetime is None

    @patch(f'{_COMMAND_MODULE}.current_app')
    @patch('django_spire.celery.models.CeleryTask.async_result', new_callable=PropertyMock)
    def test_inspect_unavailable_skips_all(
        self, mock_async_result: PropertyMock, mock_app: MagicMock
    ) -> None:
        celery_task = _with_last_update(
            create_test_celery_task(state=states.STARTED), time.time() - 700
        )
        mock_async_result.return_value = SimpleNamespace(state=states.STARTED)
        mock_app.control.inspect.side_effect = ConnectionError('broker down')

        call_command('prune_stale_started_celery_tasks')

        celery_task.refresh_from_db()
        assert celery_task.state == states.STARTED

    @patch(f'{_COMMAND_MODULE}.current_app')
    @patch('django_spire.celery.models.CeleryTask.async_result', new_callable=PropertyMock)
    def test_backend_read_error_skips_celery_task(
        self, mock_async_result: PropertyMock, mock_app: MagicMock
    ) -> None:
        celery_task = _with_last_update(
            create_test_celery_task(state=states.STARTED), time.time() - 700
        )
        mock_async_result.return_value = _BackendDownResult()
        _fake_active_inspect(mock_app, {})

        call_command('prune_stale_started_celery_tasks')

        celery_task.refresh_from_db()
        assert celery_task.state == states.STARTED
