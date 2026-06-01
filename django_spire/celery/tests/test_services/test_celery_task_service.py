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

    def test_update_result_sets_state_to_success(self) -> None:
        self.celery_task.state = states.STARTED
        self.celery_task.save()

        mock_result = MagicMock()
        mock_result.state = states.SUCCESS
        mock_result.get.return_value = 'test_result'
        mock_result.date_done = now()

        self.service.update_result(mock_result)

        self.assertEqual(self.celery_task.state, states.SUCCESS)

    def test_update_result_sets_completed_datetime(self) -> None:
        completed_time = now()
        mock_result = MagicMock()
        mock_result.state = states.SUCCESS
        mock_result.get.return_value = 'test_result'
        mock_result.date_done = completed_time

        self.service.update_result(mock_result)

        self.assertIsNotNone(self.celery_task.completed_datetime)

    def test_update_result_with_naive_datetime_makes_aware(self) -> None:
        naive_datetime = now()
        mock_result = MagicMock()
        mock_result.state = states.SUCCESS
        mock_result.get.return_value = 'test_result'
        mock_result.date_done = naive_datetime.replace(tzinfo=None)

        self.service.update_result(mock_result)

        self.assertTrue(self.celery_task.completed_datetime.tzinfo is not None)


class CeleryTaskServiceUpdateFromAsyncResultTestCase(TestCase):
    def setUp(self) -> None:
        self.celery_task = create_test_celery_task(state=states.STARTED)
        self.service = CeleryTaskService(obj=self.celery_task)

    @patch.object(CeleryTask, 'async_result', new_callable=PropertyMock)
    def test_update_from_async_result_saves_on_state_change(self, mock_async_result) -> None:
        mock_result = MagicMock()
        mock_result.state = states.FAILURE
        mock_result.ready.return_value = False
        mock_result.info = None
        mock_async_result.return_value = mock_result

        with patch.object(self.celery_task, 'save') as mock_save:
            self.service.update_from_async_result_and_save_if_change()

            mock_save.assert_called()

    @patch.object(CeleryTask, 'async_result', new_callable=PropertyMock)
    def test_update_from_async_result_pending_to_started(self, mock_async_result) -> None:
        self.celery_task.state = states.PENDING
        self.celery_task.save()

        mock_result = MagicMock()
        mock_result.state = states.STARTED
        mock_result.ready.return_value = False
        mock_result.info = None
        mock_async_result.return_value = mock_result

        self.service.update_from_async_result_and_save_if_change()

        self.assertEqual(self.celery_task.state, states.STARTED)