from __future__ import annotations

import uuid
from datetime import timedelta
from unittest.mock import MagicMock, patch

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