from __future__ import annotations

import pickle
import uuid
from unittest.mock import MagicMock, patch

from celery import states
from django.test import TestCase, override_settings

from django_spire.celery.manager import BaseCeleryTaskManager
from django_spire.celery.models import CeleryTask


SECRET_KEY = 'test-secret-key'


class ManagerTestCeleryTaskManager(BaseCeleryTaskManager):
    task_name = 'test_task'
    display_name = 'Test Task'
    estimated_completion_seconds = 60


class ManagerTestCeleryTaskManagerWithModel(BaseCeleryTaskManager):
    task_name = 'test_task_with_model'
    display_name = 'Test Task With Model'
    estimated_completion_seconds = 120


class BaseCeleryTaskManagerSendTaskRetriesValidationTestCase(TestCase):
    def test_raises_error_when_send_task_retries_exceeds_max(self) -> None:
        with self.assertRaises(ValueError) as context:
            class ExceedsMaxManager(BaseCeleryTaskManager):
                task_name = 'exceeds_max'
                display_name = 'Exceeds Max'
                send_task_retries = 10

        self.assertIn('send_task_retries', str(context.exception))
        self.assertIn('exceeded', str(context.exception))

    def test_default_send_task_retries_is_two(self) -> None:
        manager = ManagerTestCeleryTaskManager()
        self.assertEqual(manager.send_task_retries, 2)


class BaseCeleryTaskManagerRequiredAttributesTestCase(TestCase):
    def test_raises_error_when_task_name_not_set(self) -> None:
        with self.assertRaises(TypeError) as context:
            class InvalidManager(BaseCeleryTaskManager):
                display_name = 'Test'

        self.assertIn('task_name', str(context.exception))

    def test_raises_error_when_display_name_not_set(self) -> None:
        with self.assertRaises(TypeError) as context:
            class InvalidManager(BaseCeleryTaskManager):
                task_name = 'test_task'

        self.assertIn('display_name', str(context.exception))

    def test_raises_error_when_task_name_not_string(self) -> None:
        with self.assertRaises(TypeError) as context:
            class InvalidManager(BaseCeleryTaskManager):
                task_name = 123
                display_name = 'Test'

        self.assertIn('task_name', str(context.exception))

    def test_raises_error_when_display_name_not_string(self) -> None:
        with self.assertRaises(TypeError) as context:
            class InvalidManager(BaseCeleryTaskManager):
                task_name = 'test_task'
                display_name = 123

        self.assertIn('display_name', str(context.exception))


class BaseCeleryTaskManagerPropertiesTestCase(TestCase):
    @override_settings(SECRET_KEY=SECRET_KEY)
    def test_reference_key_consistency(self) -> None:
        manager = ManagerTestCeleryTaskManager()
        reference_key_1 = manager.reference_key
        reference_key_2 = manager.reference_key

        self.assertEqual(reference_key_1, reference_key_2)

    @override_settings(SECRET_KEY=SECRET_KEY)
    def test_reference_key_is_md5_hash(self) -> None:
        manager = ManagerTestCeleryTaskManager()
        reference_key = manager.reference_key

        self.assertEqual(len(reference_key), 32)

    @override_settings(SECRET_KEY=SECRET_KEY)
    def test_reference_key_different_for_different_task_names(self) -> None:
        class Manager1(BaseCeleryTaskManager):
            task_name = 'task_1'
            display_name = 'Task 1'

        class Manager2(BaseCeleryTaskManager):
            task_name = 'task_2'
            display_name = 'Task 2'

        manager1 = Manager1()
        manager2 = Manager2()

        self.assertNotEqual(manager1.reference_key, manager2.reference_key)

    @override_settings(SECRET_KEY=SECRET_KEY)
    def test_reference_key_different_for_different_class_names(self) -> None:
        class Manager1(BaseCeleryTaskManager):
            task_name = 'same_task'
            display_name = 'Same Task'

        class Manager2(BaseCeleryTaskManager):
            task_name = 'same_task'
            display_name = 'Same Task'

        manager1 = Manager1()
        manager2 = Manager2()

        self.assertNotEqual(manager1.reference_key, manager2.reference_key)

    @override_settings(SECRET_KEY=SECRET_KEY)
    def test_model_key_none_when_no_model_object(self) -> None:
        manager = ManagerTestCeleryTaskManager()

        self.assertIsNone(manager.model_key)

    @override_settings(SECRET_KEY=SECRET_KEY)
    def test_model_key_generated_when_model_object_set(self) -> None:
        mock_model = MagicMock()
        mock_model.pk = 123

        manager = ManagerTestCeleryTaskManagerWithModel(model_object=mock_model)
        model_key = manager.model_key

        self.assertIsNotNone(model_key)
        self.assertEqual(len(model_key), 32)

    @override_settings(SECRET_KEY=SECRET_KEY)
    def test_model_key_consistency(self) -> None:
        mock_model = MagicMock()
        mock_model.pk = 123

        manager = ManagerTestCeleryTaskManagerWithModel(model_object=mock_model)
        model_key_1 = manager.model_key
        model_key_2 = manager.model_key

        self.assertEqual(model_key_1, model_key_2)

    @override_settings(SECRET_KEY=SECRET_KEY)
    def test_reference_and_model_key_without_model(self) -> None:
        manager = ManagerTestCeleryTaskManager()

        combined = manager.reference_and_model_key

        self.assertEqual(combined, manager.reference_key)

    @override_settings(SECRET_KEY=SECRET_KEY)
    def test_reference_and_model_key_with_model(self) -> None:
        mock_model = MagicMock()
        mock_model.pk = 123

        manager = ManagerTestCeleryTaskManagerWithModel(model_object=mock_model)

        combined = manager.reference_and_model_key

        self.assertIn(manager.reference_key, combined)
        self.assertIn('|', combined)

    @override_settings(SECRET_KEY=SECRET_KEY)
    def test_class_and_send_task_method(self) -> None:
        manager = ManagerTestCeleryTaskManager()

        method = manager.class_and_send_task_method

        self.assertIn('ManagerTestCeleryTaskManager', method)
        self.assertIn('send_task', method)


class BaseCeleryTaskManagerValidationTestCase(TestCase):
    def test_validates_required_args_count(self) -> None:
        class StrictManager(BaseCeleryTaskManager):
            task_name = 'strict_task'
            display_name = 'Strict Task'
            required_args_types = [int, str]

        manager = StrictManager()

        with self.assertRaises(ValueError) as context:
            manager._validate_args_and_kwargs(1)

        self.assertIn('only got 1 arguments', str(context.exception))

    def test_validates_required_args_types(self) -> None:
        class StrictManager(BaseCeleryTaskManager):
            task_name = 'strict_task'
            display_name = 'Strict Task'
            required_args_types = [int, str]

        manager = StrictManager()

        with self.assertRaises(TypeError) as context:
            manager._validate_args_and_kwargs('string', 123)

        self.assertIn('invalid type', str(context.exception))

    def test_validates_required_kwargs_keys(self) -> None:
        class StrictManager(BaseCeleryTaskManager):
            task_name = 'strict_task'
            display_name = 'Strict Task'
            required_kwargs_keys_types = {'name': str, 'count': int}

        manager = StrictManager()

        with self.assertRaises(ValueError) as context:
            manager._validate_args_and_kwargs(name='test')

        self.assertIn('missing kwarg "count"', str(context.exception))

    def test_validates_required_kwargs_types(self) -> None:
        class StrictManager(BaseCeleryTaskManager):
            task_name = 'strict_task'
            display_name = 'Strict Task'
            required_kwargs_keys_types = {'name': str, 'count': int}

        manager = StrictManager()

        with self.assertRaises(TypeError) as context:
            manager._validate_args_and_kwargs(name='test', count='not_int')

        self.assertIn('invalid type', str(context.exception))

    def test_validation_passes_when_no_requirements(self) -> None:
        manager = ManagerTestCeleryTaskManager()

        manager._validate_args_and_kwargs(1, 2, 3, key='value')


class BaseCeleryTaskManagerSendTaskTestCase(TestCase):
    @override_settings(SECRET_KEY=SECRET_KEY)
    @patch('django_spire.celery.manager.send_task')
    def test_send_task_creates_celery_task_record(self, mock_send_task) -> None:
        valid_uuid = uuid.uuid4()
        mock_async_result = MagicMock()
        mock_async_result.id = str(valid_uuid)
        mock_send_task.return_value = mock_async_result

        manager = ManagerTestCeleryTaskManager()
        celery_task = manager.send_task(1, 2, 3)

        self.assertIsInstance(celery_task, CeleryTask)
        self.assertEqual(celery_task.task_name, 'test_task')
        self.assertEqual(celery_task.display_name, 'Test Task')

    @override_settings(SECRET_KEY=SECRET_KEY)
    @patch('django_spire.celery.manager.send_task')
    def test_send_task_with_estimated_time(self, mock_send_task) -> None:
        valid_uuid = uuid.uuid4()
        mock_async_result = MagicMock()
        mock_async_result.id = str(valid_uuid)
        mock_send_task.return_value = mock_async_result

        manager = ManagerTestCeleryTaskManager()
        celery_task = manager.send_task()

        self.assertIsNotNone(celery_task.estimated_completion_datetime)

    @override_settings(SECRET_KEY=SECRET_KEY)
    @patch('django_spire.celery.manager.send_task')
    def test_send_task_passes_args_to_celery(self, mock_send_task) -> None:
        valid_uuid = uuid.uuid4()
        mock_async_result = MagicMock()
        mock_async_result.id = str(valid_uuid)
        mock_send_task.return_value = mock_async_result

        manager = ManagerTestCeleryTaskManager()
        manager.send_task('arg1', 'arg2')

        mock_send_task.assert_called_once()
        call_kwargs = mock_send_task.call_args[1]
        self.assertEqual(call_kwargs['args'], ('arg1', 'arg2'))

    @override_settings(SECRET_KEY=SECRET_KEY)
    @patch('django_spire.celery.manager.send_task')
    def test_send_task_passes_kwargs_to_celery(self, mock_send_task) -> None:
        valid_uuid = uuid.uuid4()
        mock_async_result = MagicMock()
        mock_async_result.id = str(valid_uuid)
        mock_send_task.return_value = mock_async_result

        manager = ManagerTestCeleryTaskManager()
        manager.send_task(key='value')

        mock_send_task.assert_called_once()
        call_kwargs = mock_send_task.call_args[1]
        self.assertEqual(call_kwargs['kwargs'], {'key': 'value'})


class BaseCeleryTaskManagerFilterCeleryTasksTestCase(TestCase):
    @override_settings(SECRET_KEY=SECRET_KEY)
    def test_filter_celery_tasks_returns_queryset(self) -> None:
        manager = ManagerTestCeleryTaskManager()

        result = manager.filter_celery_tasks()

        self.assertIsNotNone(result)


class BaseCeleryTaskManagerRetryConfigTestCase(TestCase):
    def test_default_retry_config_values(self) -> None:
        manager = ManagerTestCeleryTaskManager()

        self.assertEqual(manager.send_task_retries, 2)

    def test_can_override_retry_config_via_class_attributes(self) -> None:
        class CustomRetryManager(BaseCeleryTaskManager):
            task_name = 'custom_retry_task'
            display_name = 'Custom Retry Task'
            send_task_retries = 4

        manager = CustomRetryManager()

        self.assertEqual(manager.send_task_retries, 4)

    def test_can_override_retry_config_per_call(self) -> None:
        manager = ManagerTestCeleryTaskManager()

        self.assertEqual(manager.send_task_retries, 2)


class BaseCeleryTaskManagerRetryTestCase(TestCase):
    @override_settings(SECRET_KEY=SECRET_KEY)
    @patch('django_spire.celery.manager.time.sleep')
    @patch('django_spire.celery.manager.send_task')
    def test_retries_on_connection_error(self, mock_send_task: MagicMock, mock_sleep: MagicMock) -> None:
        from kombu.exceptions import OperationalError as KombuOperationalError

        valid_uuid = uuid.uuid4()
        mock_async_result = MagicMock()
        mock_async_result.id = str(valid_uuid)

        mock_send_task.side_effect = [
            KombuOperationalError('Connection failed'),
            KombuOperationalError('Connection failed'),
            mock_async_result,
        ]

        manager = ManagerTestCeleryTaskManager()
        celery_task = manager.send_task(1, 2, 3)

        self.assertEqual(mock_send_task.call_count, 3)
        self.assertEqual(mock_sleep.call_count, 2)
        self.assertIsInstance(celery_task, CeleryTask)

    @override_settings(SECRET_KEY=SECRET_KEY)
    @patch('django_spire.celery.manager.time.sleep')
    @patch('django_spire.celery.manager.send_task')
    def test_respects_send_task_retries_class_attribute(self, mock_send_task: MagicMock, mock_sleep: MagicMock) -> None:
        from kombu.exceptions import OperationalError as KombuOperationalError

        class LowRetryManager(BaseCeleryTaskManager):
            task_name = 'low_retry_task'
            display_name = 'Low Retry Task'
            send_task_retries = 1

        mock_send_task.side_effect = KombuOperationalError('Connection failed')

        manager = LowRetryManager()
        celery_task = manager.send_task()

        self.assertEqual(mock_send_task.call_count, 2)
        self.assertEqual(mock_sleep.call_count, 1)

    @override_settings(SECRET_KEY=SECRET_KEY)
    @patch('django_spire.celery.manager.time.sleep')
    @patch('django_spire.celery.manager.send_task')
    def test_respects_send_task_retries_per_call_override(self, mock_send_task: MagicMock, mock_sleep: MagicMock) -> None:
        from kombu.exceptions import OperationalError as KombuOperationalError

        mock_send_task.side_effect = KombuOperationalError('Connection failed')

        manager = ManagerTestCeleryTaskManager()
        celery_task = manager.send_task(send_task_retries=1)

        self.assertEqual(mock_send_task.call_count, 2)
        self.assertEqual(mock_sleep.call_count, 1)

    @override_settings(SECRET_KEY=SECRET_KEY)
    @patch('django_spire.celery.manager.time.sleep')
    @patch('django_spire.celery.manager.send_task')
    def test_exponential_backoff_calculation(self, mock_send_task: MagicMock, mock_sleep: MagicMock) -> None:
        from kombu.exceptions import OperationalError as KombuOperationalError

        valid_uuid = uuid.uuid4()
        mock_async_result = MagicMock()
        mock_async_result.id = str(valid_uuid)

        mock_send_task.side_effect = [
            KombuOperationalError('Failed'),
            KombuOperationalError('Failed'),
            mock_async_result,
        ]

        manager = ManagerTestCeleryTaskManager()
        manager.send_task()

        self.assertEqual(mock_sleep.call_count, 2)
        self.assertEqual(mock_sleep.call_args_list[0][0][0], 1)
        self.assertEqual(mock_sleep.call_args_list[1][0][0], 2)

    @override_settings(SECRET_KEY=SECRET_KEY)
    @patch('django_spire.celery.manager.send_task')
    def test_no_retry_when_send_task_retries_is_zero(self, mock_send_task: MagicMock) -> None:
        from kombu.exceptions import OperationalError as KombuOperationalError

        mock_send_task.side_effect = KombuOperationalError('Failed')

        manager = ManagerTestCeleryTaskManager()
        celery_task = manager.send_task(send_task_retries=0)

        self.assertEqual(mock_send_task.call_count, 1)
        self.assertTrue(celery_task.send_failed)

    @override_settings(SECRET_KEY=SECRET_KEY)
    @patch('django_spire.celery.manager.send_task')
    def test_no_retry_when_send_task_retries_is_zero_class_attribute(self, mock_send_task: MagicMock) -> None:
        from kombu.exceptions import OperationalError as KombuOperationalError

        class NoRetryManager(BaseCeleryTaskManager):
            task_name = 'no_retry_task'
            display_name = 'No Retry Task'
            send_task_retries = 0

        mock_send_task.side_effect = KombuOperationalError('Failed')

        manager = NoRetryManager()
        celery_task = manager.send_task()

        self.assertEqual(mock_send_task.call_count, 1)
        self.assertTrue(celery_task.send_failed)


class BaseCeleryTaskManagerFailSafeTestCase(TestCase):
    @override_settings(SECRET_KEY=SECRET_KEY)
    @patch('django_spire.celery.manager.send_task')
    def test_creates_failed_record_after_max_retries(self, mock_send_task: MagicMock) -> None:
        from kombu.exceptions import OperationalError as KombuOperationalError

        mock_send_task.side_effect = KombuOperationalError('Connection failed')

        manager = ManagerTestCeleryTaskManager()
        celery_task = manager.send_task(send_task_retries=2)

        self.assertIsInstance(celery_task, CeleryTask)
        self.assertEqual(celery_task.state, states.FAILURE)
        self.assertTrue(celery_task.send_failed)
        self.assertTrue(celery_task.has_result)

    @override_settings(SECRET_KEY=SECRET_KEY)
    @patch('django_spire.celery.manager.send_task')
    def test_failed_record_contains_error_message(self, mock_send_task: MagicMock) -> None:
        from kombu.exceptions import OperationalError as KombuOperationalError

        mock_send_task.side_effect = KombuOperationalError('RabbitMQ connection refused')

        manager = ManagerTestCeleryTaskManager()
        celery_task = manager.send_task()

        self.assertIn('RabbitMQ connection refused', celery_task.send_error_message)

    @override_settings(SECRET_KEY=SECRET_KEY)
    @patch('django_spire.celery.manager.send_task')
    def test_failed_record_has_send_failed_error_type(self, mock_send_task: MagicMock) -> None:
        from kombu.exceptions import OperationalError as KombuOperationalError

        mock_send_task.side_effect = KombuOperationalError('Failed')

        manager = ManagerTestCeleryTaskManager()
        celery_task = manager.send_task()

        self.assertTrue(celery_task.send_failed)
        result_data = celery_task.send_error_details
        self.assertEqual(result_data['task_name'], 'test_task')

    @override_settings(SECRET_KEY=SECRET_KEY)
    @patch('django_spire.celery.manager.send_task')
    def test_failed_record_preserves_original_args_kwargs(self, mock_send_task: MagicMock) -> None:
        from kombu.exceptions import OperationalError as KombuOperationalError

        mock_send_task.side_effect = KombuOperationalError('Failed')

        manager = ManagerTestCeleryTaskManager()
        celery_task = manager.send_task('arg1', 'arg2', key='value')

        self.assertEqual(celery_task.send_error_details['args'], ('arg1', 'arg2'))
        self.assertEqual(celery_task.send_error_details['kwargs'], {'key': 'value'})

    @override_settings(SECRET_KEY=SECRET_KEY)
    @patch('django_spire.celery.manager.send_task')
    def test_can_distinguish_send_failure_from_task_failure(self, mock_send_task: MagicMock) -> None:
        valid_uuid = uuid.uuid4()
        mock_async_result = MagicMock()
        mock_async_result.id = str(valid_uuid)
        mock_send_task.return_value = mock_async_result

        manager = ManagerTestCeleryTaskManager()

        success_task = manager.send_task()
        self.assertFalse(success_task.send_failed)
        self.assertIsNone(success_task.send_error_message)

    @override_settings(SECRET_KEY=SECRET_KEY)
    @patch('django_spire.celery.manager.send_task')
    def test_failed_task_result_returns_error_data(self, mock_send_task: MagicMock) -> None:
        from kombu.exceptions import OperationalError as KombuOperationalError

        mock_send_task.side_effect = KombuOperationalError('Connection lost')

        manager = ManagerTestCeleryTaskManager()
        celery_task = manager.send_task(data_id=123)

        self.assertEqual(celery_task.result['error'], 'SEND_FAILED')
        self.assertEqual(celery_task.result['message'], 'Connection lost')
        self.assertEqual(celery_task.result['kwargs'], {'data_id': 123})

    @override_settings(SECRET_KEY=SECRET_KEY)
    @patch('django_spire.celery.manager.send_task')
    def test_multiple_consecutive_failures_all_recorded(self, mock_send_task: MagicMock) -> None:
        from kombu.exceptions import OperationalError as KombuOperationalError

        mock_send_task.side_effect = KombuOperationalError('Failed')

        manager = ManagerTestCeleryTaskManager()

        tasks = []
        for _ in range(3):
            tasks.append(manager.send_task())

        for task in tasks:
            self.assertTrue(task.send_failed)
            self.assertIsNotNone(task.send_error_message)