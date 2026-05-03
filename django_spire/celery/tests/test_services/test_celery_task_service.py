from __future__ import annotations

from unittest.mock import MagicMock, patch, PropertyMock

from celery import states
from django.test import TestCase
from django.utils.timezone import now

from django_spire.celery.models import CeleryTask
from django_spire.celery.services.service import CeleryTaskService
from django_spire.celery.tests.factories import create_test_celery_task


class CeleryTaskServiceUpdateResultTestCase(TestCase):
    def setUp(self) -> None:
        self.celery_task = create_test_celery_task()
        self.service = CeleryTaskService(obj=self.celery_task)

    @patch.object(CeleryTask, 'async_result', new_callable=PropertyMock)
    def test_update_result_sets_has_result_true_on_success(self, mock_async_result) -> None:
        mock_result = MagicMock()
        mock_result.state = states.SUCCESS
        mock_result.get.return_value = {'key': 'value'}
        mock_result.date_done = now()
        mock_async_result.return_value = mock_result

        self.service.update_result()

        self.celery_task.refresh_from_db()
        self.assertTrue(self.celery_task.has_result)

    @patch.object(CeleryTask, 'async_result', new_callable=PropertyMock)
    def test_update_result_sets_completed_datetime(self, mock_async_result) -> None:
        completed_time = now()
        mock_result = MagicMock()
        mock_result.state = states.SUCCESS
        mock_result.get.return_value = 'test_result'
        mock_result.date_done = completed_time
        mock_async_result.return_value = mock_result

        self.service.update_result()

        self.celery_task.refresh_from_db()
        self.assertIsNotNone(self.celery_task.completed_datetime)

    @patch.object(CeleryTask, 'async_result', new_callable=PropertyMock)
    def test_update_result_sets_state_to_success(self, mock_async_result) -> None:
        self.celery_task.state = states.STARTED
        self.celery_task.save()

        mock_result = MagicMock()
        mock_result.state = states.SUCCESS
        mock_result.get.return_value = 'test_result'
        mock_result.date_done = now()
        mock_async_result.return_value = mock_result

        self.service.update_result()

        self.celery_task.refresh_from_db()
        self.assertEqual(self.celery_task.state, states.SUCCESS)

    @patch.object(CeleryTask, 'async_result', new_callable=PropertyMock)
    def test_update_result_with_naive_datetime_makes_aware(self, mock_async_result) -> None:
        naive_datetime = now()
        mock_result = MagicMock()
        mock_result.state = states.SUCCESS
        mock_result.get.return_value = 'test_result'
        mock_result.date_done = naive_datetime.replace(tzinfo=None)
        mock_async_result.return_value = mock_result

        self.service.update_result()

        self.celery_task.refresh_from_db()
        self.assertTrue(self.celery_task.completed_datetime.tzinfo is not None)

    @patch.object(CeleryTask, 'async_result', new_callable=PropertyMock)
    def test_update_result_does_not_save_if_not_success_state(self, mock_async_result) -> None:
        mock_result = MagicMock()
        mock_result.state = states.PENDING
        mock_async_result.return_value = mock_result

        self.service.update_result()

        self.celery_task.refresh_from_db()
        self.assertFalse(self.celery_task.has_result)


class CeleryTaskServiceUpdateResultDatabaseErrorTestCase(TestCase):
    def setUp(self) -> None:
        self.celery_task = create_test_celery_task()
        self.service = CeleryTaskService(obj=self.celery_task)

    @patch.object(CeleryTask, 'async_result', new_callable=PropertyMock)
    def test_update_result_increments_attempts_on_db_error(self, mock_async_result) -> None:
        self.celery_task._result_capture_attempts = 2
        self.celery_task.save()

        mock_result = MagicMock()
        mock_result.state = states.SUCCESS
        from sqlalchemy.exc import OperationalError
        mock_result.get.side_effect = OperationalError('statement', {}, Exception('error'))
        mock_result.date_done = now()
        mock_async_result.return_value = mock_result

        try:
            self.service.update_result()
        except Exception:
            pass

        self.celery_task.refresh_from_db()
        self.assertEqual(self.celery_task._result_capture_attempts, 3)

    @patch.object(CeleryTask, 'async_result', new_callable=PropertyMock)
    def test_update_result_sets_failure_state_after_max_attempts(self, mock_async_result) -> None:
        self.celery_task._result_capture_attempts = 4
        self.celery_task.save()

        mock_result = MagicMock()
        mock_result.state = states.SUCCESS
        from sqlalchemy.exc import OperationalError
        mock_result.get.side_effect = OperationalError('statement', {}, Exception('error'))
        mock_result.date_done = now()
        mock_async_result.return_value = mock_result

        try:
            self.service.update_result()
        except Exception:
            pass

        self.celery_task.refresh_from_db()
        self.assertEqual(self.celery_task.state, states.FAILURE)


class CeleryTaskServiceUpdateFromAsyncResultTestCase(TestCase):
    def setUp(self) -> None:
        self.celery_task = create_test_celery_task(state=states.STARTED)
        self.service = CeleryTaskService(obj=self.celery_task)

    @patch.object(CeleryTask, 'async_result', new_callable=PropertyMock)
    def test_update_from_async_result_calls_update_result_on_success(self, mock_async_result) -> None:
        mock_result = MagicMock()
        mock_result.state = states.SUCCESS
        mock_result.get.return_value = 'test_result'
        mock_result.date_done = now()
        mock_async_result.return_value = mock_result

        with patch.object(self.service, 'update_result') as mock_update:
            self.service.update_from_async_result_and_save_if_change()

            mock_update.assert_called_once()

    @patch.object(CeleryTask, 'async_result', new_callable=PropertyMock)
    def test_update_from_async_result_saves_on_state_change(self, mock_async_result) -> None:
        mock_result = MagicMock()
        mock_result.state = states.FAILURE
        mock_async_result.return_value = mock_result

        with patch.object(self.celery_task, 'save') as mock_save:
            self.service.update_from_async_result_and_save_if_change()

            mock_save.assert_called()

    @patch.object(CeleryTask, 'async_result', new_callable=PropertyMock)
    def test_update_from_async_result_does_not_save_when_state_unchanged(self, mock_async_result) -> None:
        mock_result = MagicMock()
        mock_result.state = states.STARTED
        mock_async_result.return_value = mock_result

        self.celery_task.state = states.STARTED
        self.celery_task.save()

        with patch.object(self.celery_task, 'save') as mock_save:
            self.service.update_from_async_result_and_save_if_change()

            mock_save.assert_not_called()

    @patch.object(CeleryTask, 'async_result', new_callable=PropertyMock)
    def test_update_from_async_result_already_success_does_not_update(self, mock_async_result) -> None:
        self.celery_task.state = states.SUCCESS
        self.celery_task.save()

        mock_result = MagicMock()
        mock_result.state = states.SUCCESS
        mock_async_result.return_value = mock_result

        with patch.object(self.service, 'update_result') as mock_update:
            self.service.update_from_async_result_and_save_if_change()

            mock_update.assert_not_called()

    @patch.object(CeleryTask, 'async_result', new_callable=PropertyMock)
    def test_update_from_async_result_pending_to_started(self, mock_async_result) -> None:
        self.celery_task.state = states.PENDING
        self.celery_task.save()

        mock_result = MagicMock()
        mock_result.state = states.STARTED
        mock_async_result.return_value = mock_result

        self.service.update_from_async_result_and_save_if_change()

        self.celery_task.refresh_from_db()
        self.assertEqual(self.celery_task.state, states.STARTED)