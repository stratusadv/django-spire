from __future__ import annotations

from datetime import datetime
from unittest.mock import MagicMock, patch, PropertyMock
from uuid import uuid4

from celery import states
from celery.result import AsyncResult
from django.test import TestCase
from django.utils.timezone import now

from django_spire.celery.models import CeleryTask, _celery_state_choices
from django_spire.celery.tests.factories import create_test_celery_task


class AsyncResultPropertyTestCase(TestCase):
    def test_async_result_returns_async_result_instance(self) -> None:
        task = create_test_celery_task()

        result = task.async_result

        self.assertIsInstance(result, AsyncResult)

    def test_async_result_uses_task_id_as_id(self) -> None:
        task = create_test_celery_task()

        result = task.async_result

        self.assertEqual(result.id, str(task.task_id))

    def test_async_result_id_matches_task_uuid(self) -> None:
        task_id = uuid4()
        task = create_test_celery_task(task_id=task_id)

        result = task.async_result

        self.assertEqual(result.id, str(task_id))


class AsyncResultStatesTestCase(TestCase):
    def test_celery_state_choices_returns_list(self) -> None:
        choices = _celery_state_choices()

        self.assertIsInstance(choices, list)
        self.assertTrue(len(choices) > 0)

    def test_celery_state_choices_contains_tuple_with_title(self) -> None:
        choices = _celery_state_choices()

        for choice in choices:
            self.assertIsInstance(choice, tuple)
            self.assertEqual(len(choice), 2)
            self.assertIsInstance(choice[1], str)

    def test_celery_state_choices_all_states_are_strings(self) -> None:
        choices = _celery_state_choices()
        states_from_choices = [choice[0] for choice in choices]

        for state in states_from_choices:
            self.assertIsInstance(state, str)

    def test_celery_state_choices_contains_all_celery_states(self) -> None:
        choices = _celery_state_choices()
        states_from_choices = [choice[0] for choice in choices]

        for celery_state in states.ALL_STATES:
            self.assertIn(celery_state, states_from_choices)


class AsyncResultModelStateMappingTestCase(TestCase):
    def test_is_processing_for_pending(self) -> None:
        task = create_test_celery_task(state=states.PENDING)

        self.assertTrue(task.is_processing)

    def test_is_processing_for_started(self) -> None:
        task = create_test_celery_task(state=states.STARTED)

        self.assertTrue(task.is_processing)

    def test_is_processing_for_received(self) -> None:
        task = create_test_celery_task(state=states.RECEIVED)

        self.assertTrue(task.is_processing)

    def test_is_processing_for_retry(self) -> None:
        task = create_test_celery_task(state=states.RETRY)

        self.assertTrue(task.is_processing)

    def test_is_processing_false_for_success(self) -> None:
        task = create_test_celery_task(state=states.SUCCESS)

        self.assertFalse(task.is_processing)

    def test_is_processing_false_for_failure(self) -> None:
        task = create_test_celery_task(state=states.FAILURE)

        self.assertFalse(task.is_processing)

    def test_is_processing_false_for_revoked(self) -> None:
        task = create_test_celery_task(state=states.REVOKED)

        self.assertFalse(task.is_processing)


class AsyncResultServiceIntegrationTestCase(TestCase):
    def setUp(self) -> None:
        self.celery_task = create_test_celery_task(state=states.STARTED)
        self.service = self.celery_task.services

    @patch.object(CeleryTask, 'async_result', new_callable=PropertyMock)
    def test_update_result_from_successful_async_result(self, mock_async_result) -> None:
        expected_result = {'data': 'test_value'}
        completed_time = now()

        mock_result = MagicMock()
        mock_result.state = states.SUCCESS
        mock_result.get.return_value = expected_result
        mock_result.date_done = completed_time
        mock_async_result.return_value = mock_result

        self.service.update_result()

        self.celery_task.refresh_from_db()
        self.assertTrue(self.celery_task.has_result)
        self.assertEqual(self.celery_task.state, states.SUCCESS)

    @patch.object(CeleryTask, 'async_result', new_callable=PropertyMock)
    def test_update_from_async_result_pending_to_success(self, mock_async_result) -> None:
        self.celery_task.state = states.PENDING
        self.celery_task.save()

        completed_time = now()
        mock_result = MagicMock()
        mock_result.state = states.SUCCESS
        mock_result.get.return_value = 'success_result'
        mock_result.date_done = completed_time
        mock_async_result.return_value = mock_result

        self.service.update_from_async_result_and_save_if_change()

        self.celery_task.refresh_from_db()
        self.assertEqual(self.celery_task.state, states.SUCCESS)

    @patch.object(CeleryTask, 'async_result', new_callable=PropertyMock)
    def test_update_from_async_result_started_to_failure(self, mock_async_result) -> None:
        mock_result = MagicMock()
        mock_result.state = states.FAILURE
        mock_async_result.return_value = mock_result

        self.service.update_from_async_result_and_save_if_change()

        self.celery_task.refresh_from_db()
        self.assertEqual(self.celery_task.state, states.FAILURE)

    @patch.object(CeleryTask, 'async_result', new_callable=PropertyMock)
    def test_update_from_async_result_does_not_overwrite_success(self, mock_async_result) -> None:
        self.celery_task.state = states.SUCCESS
        self.celery_task.has_result = True
        self.celery_task.save()

        mock_result = MagicMock()
        mock_result.state = states.SUCCESS
        mock_async_result.return_value = mock_result

        with patch.object(self.service, 'update_result') as mock_update:
            self.service.update_from_async_result_and_save_if_change()

            mock_update.assert_not_called()


class AsyncResultResultHandlingTestCase(TestCase):
    def test_result_returns_none_for_failure_state(self) -> None:
        task = create_test_celery_task(state=states.FAILURE)

        result = task.result

        self.assertIsNone(result)

    def test_result_returns_deserialized_data(self) -> None:
        import pickle

        task = create_test_celery_task()
        test_data = {
            'string': 'test',
            'number': 42,
            'list': [1, 2, 3],
            'nested': {'key': 'value'},
        }
        task._result = pickle.dumps(test_data)
        task.has_result = True
        task.save()

        result = task.result

        self.assertEqual(result, test_data)


class AsyncResultWithMockedCeleryBackendTestCase(TestCase):
    @patch.object(CeleryTask, 'async_result', new_callable=PropertyMock)
    def test_async_result_backend_access(self, mock_async_result) -> None:
        task = create_test_celery_task()

        mock_result = MagicMock()
        mock_result.state = states.PENDING
        mock_result.ready.return_value = False
        mock_result.successful.return_value = False
        mock_async_result.return_value = mock_result

        async_result = task.async_result

        self.assertFalse(async_result.ready())
        self.assertFalse(async_result.successful())

    @patch.object(CeleryTask, 'async_result', new_callable=PropertyMock)
    def test_async_result_get_returns_value(self, mock_async_result) -> None:
        task = create_test_celery_task()

        expected_value = 'test_task_result'
        mock_result = MagicMock()
        mock_result.state = states.SUCCESS
        mock_result.get.return_value = expected_value
        mock_async_result.return_value = mock_result

        async_result = task.async_result
        result = async_result.get()

        self.assertEqual(result, expected_value)

    @patch.object(CeleryTask, 'async_result', new_callable=PropertyMock)
    def test_async_result_wait_for_result(self, mock_async_result) -> None:
        task = create_test_celery_task()

        mock_result = MagicMock()
        mock_result.state = states.SUCCESS
        mock_result.get.return_value = 'completed'
        mock_async_result.return_value = mock_result

        async_result = task.async_result

        with patch('time.sleep'):
            result = async_result.get(timeout=1)

        self.assertEqual(result, 'completed')