from __future__ import annotations

import pickle
import uuid

import pytest

from unittest.mock import MagicMock, patch

from celery import states
from django.test import TestCase, override_settings

from django_spire.celery.manager import BaseCeleryTaskManager
from django_spire.celery.models import CeleryTask


SECRET_KEY = 'test-secret-key'


class ManagerTestCeleryTaskManager(BaseCeleryTaskManager):
    task_name = 'test_task'
    display_name = 'Test Task'


class ManagerTestCeleryTaskManagerWithModel(BaseCeleryTaskManager):
    task_name = 'test_task_with_model'
    display_name = 'Test Task With Model'


class BaseCeleryTaskManagerSendTaskRetriesValidationTestCase(TestCase):
    def test_raises_error_when_send_task_retries_exceeds_max(self) -> None:
        with pytest.raises(ValueError, match='send_task_retries') as exc_info:

            class ExceedsMaxManager(BaseCeleryTaskManager):
                task_name = 'exceeds_max'
                display_name = 'Exceeds Max'
                send_task_retries = 10

        assert 'send_task_retries' in str(exc_info.value)
        assert 'exceeded' in str(exc_info.value)

    def test_default_send_task_retries_is_two(self) -> None:
        manager = ManagerTestCeleryTaskManager()
        assert manager.send_task_retries == 2


class BaseCeleryTaskManagerRequiredAttributesTestCase(TestCase):
    def test_raises_error_when_task_name_not_set(self) -> None:
        with pytest.raises(TypeError) as exc_info:

            class InvalidManager(BaseCeleryTaskManager):
                display_name = 'Test'

        assert 'task_name' in str(exc_info.value)

    def test_raises_error_when_display_name_not_set(self) -> None:
        with pytest.raises(TypeError) as exc_info:

            class InvalidManager(BaseCeleryTaskManager):
                task_name = 'test_task'

        assert 'display_name' in str(exc_info.value)

    def test_raises_error_when_task_name_not_string(self) -> None:
        with pytest.raises(TypeError) as exc_info:

            class InvalidManager(BaseCeleryTaskManager):
                task_name = 123
                display_name = 'Test'

        assert 'task_name' in str(exc_info.value)

    def test_raises_error_when_display_name_not_string(self) -> None:
        with pytest.raises(TypeError) as exc_info:

            class InvalidManager(BaseCeleryTaskManager):
                task_name = 'test_task'
                display_name = 123

        assert 'display_name' in str(exc_info.value)


class BaseCeleryTaskManagerPropertiesTestCase(TestCase):
    @override_settings(SECRET_KEY=SECRET_KEY)
    def test_reference_key_consistency(self) -> None:
        manager = ManagerTestCeleryTaskManager()
        reference_key_1 = manager.reference_key
        reference_key_2 = manager.reference_key

        assert reference_key_1 == reference_key_2

    @override_settings(SECRET_KEY=SECRET_KEY)
    def test_reference_key_is_md5_hash(self) -> None:
        manager = ManagerTestCeleryTaskManager()
        reference_key = manager.reference_key

        assert len(reference_key) == 32

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

        assert manager1.reference_key != manager2.reference_key

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

        assert manager1.reference_key != manager2.reference_key

    @override_settings(SECRET_KEY=SECRET_KEY)
    def test_model_key_none_when_no_model_object(self) -> None:
        manager = ManagerTestCeleryTaskManager()

        assert manager.model_key is None

    @override_settings(SECRET_KEY=SECRET_KEY)
    def test_model_key_generated_when_model_object_set(self) -> None:
        mock_model = MagicMock()
        mock_model.pk = 123

        manager = ManagerTestCeleryTaskManagerWithModel(model_object=mock_model)
        model_key = manager.model_key

        assert model_key is not None
        assert len(model_key) == 32

    @override_settings(SECRET_KEY=SECRET_KEY)
    def test_model_key_consistency(self) -> None:
        mock_model = MagicMock()
        mock_model.pk = 123

        manager = ManagerTestCeleryTaskManagerWithModel(model_object=mock_model)
        model_key_1 = manager.model_key
        model_key_2 = manager.model_key

        assert model_key_1 == model_key_2

    @override_settings(SECRET_KEY=SECRET_KEY)
    def test_reference_and_model_key_without_model(self) -> None:
        manager = ManagerTestCeleryTaskManager()

        combined = manager.reference_and_model_key

        assert combined == manager.reference_key

    @override_settings(SECRET_KEY=SECRET_KEY)
    def test_reference_and_model_key_with_model(self) -> None:
        mock_model = MagicMock()
        mock_model.pk = 123

        manager = ManagerTestCeleryTaskManagerWithModel(model_object=mock_model)

        combined = manager.reference_and_model_key

        assert manager.reference_key in combined
        assert '|' in combined

    @override_settings(SECRET_KEY=SECRET_KEY)
    def test_class_and_send_task_method(self) -> None:
        manager = ManagerTestCeleryTaskManager()

        method = manager.class_and_send_task_method

        assert 'ManagerTestCeleryTaskManager' in method
        assert 'send_task' in method


class BaseCeleryTaskManagerValidationTestCase(TestCase):
    def test_validates_required_kwargs_keys(self) -> None:
        class StrictManager(BaseCeleryTaskManager):
            task_name = 'strict_task'
            display_name = 'Strict Task'
            required_kwargs_keys_types = {'name': str, 'count': int}

        manager = StrictManager()

        with pytest.raises(ValueError, match='missing kwarg') as exc_info:
            manager._validate_and_kwargs(name='test')

        assert 'missing kwarg "count"' in str(exc_info.value)

    def test_validates_required_kwargs_types(self) -> None:
        class StrictManager(BaseCeleryTaskManager):
            task_name = 'strict_task'
            display_name = 'Strict Task'
            required_kwargs_keys_types = {'name': str, 'count': int}

        manager = StrictManager()

        with pytest.raises(TypeError) as exc_info:
            manager._validate_and_kwargs(name='test', count='not_int')

        assert 'invalid type' in str(exc_info.value)

    def test_validation_passes_when_no_requirements(self) -> None:
        manager = ManagerTestCeleryTaskManager()

        manager._validate_and_kwargs(key='value')


class BaseCeleryTaskManagerSendTaskTestCase(TestCase):
    @override_settings(SECRET_KEY=SECRET_KEY)
    @patch('django_spire.celery.manager.send_task')
    def test_send_task_creates_celery_task_record(self, mock_send_task) -> None:
        valid_uuid = uuid.uuid4()
        mock_async_result = MagicMock()
        mock_async_result.id = str(valid_uuid)
        mock_send_task.return_value = mock_async_result

        manager = ManagerTestCeleryTaskManager()
        celery_task = manager.send_task()

        assert isinstance(celery_task, CeleryTask)
        assert celery_task.task_name == 'test_task'
        assert celery_task.display_name == 'Test Task'

    @override_settings(SECRET_KEY=SECRET_KEY)
    @patch('django_spire.celery.manager.send_task')
    def test_send_task_passes_kwargs_to_celery(self, mock_send_task) -> None:
        valid_uuid = uuid.uuid4()
        mock_async_result = MagicMock()
        mock_async_result.id = str(valid_uuid)
        mock_send_task.return_value = mock_async_result

        manager = ManagerTestCeleryTaskManager()
        manager.send_task(arg1='value1', arg2='value2')

        mock_send_task.assert_called_once()
        call_kwargs = mock_send_task.call_args[1]
        assert call_kwargs['kwargs'] == {'arg1': 'value1', 'arg2': 'value2'}

    @override_settings(SECRET_KEY=SECRET_KEY)
    @patch('django_spire.celery.manager.send_task')
    def test_send_task_uses_only_kwargs(self, mock_send_task) -> None:
        valid_uuid = uuid.uuid4()
        mock_async_result = MagicMock()
        mock_async_result.id = str(valid_uuid)
        mock_send_task.return_value = mock_async_result

        manager = ManagerTestCeleryTaskManager()
        manager.send_task(key='value')

        mock_send_task.assert_called_once()
        call_kwargs = mock_send_task.call_args[1]
        assert call_kwargs['kwargs'] == {'key': 'value'}


class BaseCeleryTaskManagerFilterCeleryTasksTestCase(TestCase):
    @override_settings(SECRET_KEY=SECRET_KEY)
    def test_filter_celery_tasks_returns_queryset(self) -> None:
        manager = ManagerTestCeleryTaskManager()

        result = manager.filter_celery_tasks()

        assert result is not None


class BaseCeleryTaskManagerRetryConfigTestCase(TestCase):
    def test_default_retry_config_values(self) -> None:
        manager = ManagerTestCeleryTaskManager()

        assert manager.send_task_retries == 2

    def test_can_override_retry_config_via_class_attributes(self) -> None:
        class CustomRetryManager(BaseCeleryTaskManager):
            task_name = 'custom_retry_task'
            display_name = 'Custom Retry Task'
            send_task_retries = 4

        manager = CustomRetryManager()

        assert manager.send_task_retries == 4


class BaseCeleryTaskManagerRetryTestCase(TestCase):
    @override_settings(SECRET_KEY=SECRET_KEY)
    @patch('django_spire.celery.manager.time.sleep')
    @patch('django_spire.celery.manager.send_task')
    def test_retries_on_connection_error(
        self, mock_send_task: MagicMock, mock_sleep: MagicMock
    ) -> None:
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
        celery_task = manager.send_task()

        assert mock_send_task.call_count == 3
        assert mock_sleep.call_count == 2
        assert isinstance(celery_task, CeleryTask)

    @override_settings(SECRET_KEY=SECRET_KEY)
    @patch('django_spire.celery.manager.time.sleep')
    @patch('django_spire.celery.manager.send_task')
    def test_respects_send_task_retries_class_attribute(
        self, mock_send_task: MagicMock, mock_sleep: MagicMock
    ) -> None:
        from kombu.exceptions import OperationalError as KombuOperationalError

        class LowRetryManager(BaseCeleryTaskManager):
            task_name = 'low_retry_task'
            display_name = 'Low Retry Task'
            send_task_retries = 1

        mock_send_task.side_effect = KombuOperationalError('Connection failed')

        manager = LowRetryManager()
        celery_task = manager.send_task()

        assert mock_send_task.call_count == 2
        assert mock_sleep.call_count == 1

    @override_settings(SECRET_KEY=SECRET_KEY)
    @patch('django_spire.celery.manager.time.sleep')
    @patch('django_spire.celery.manager.send_task')
    def test_exponential_backoff_calculation(
        self, mock_send_task: MagicMock, mock_sleep: MagicMock
    ) -> None:
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

        assert mock_sleep.call_count == 2
        assert mock_sleep.call_args_list[0][0][0] == 1
        assert mock_sleep.call_args_list[1][0][0] == 2

    @override_settings(SECRET_KEY=SECRET_KEY)
    @patch('django_spire.celery.manager.send_task')
    def test_no_retry_when_send_task_retries_is_zero(self, mock_send_task: MagicMock) -> None:
        from kombu.exceptions import OperationalError as KombuOperationalError

        class ZeroRetryManager(BaseCeleryTaskManager):
            task_name = 'zero_retry_task'
            display_name = 'Zero Retry Task'
            send_task_retries = 0

        mock_send_task.side_effect = KombuOperationalError('Failed')

        manager = ZeroRetryManager()
        celery_task = manager.send_task()

        assert mock_send_task.call_count == 1
        result_data = pickle.loads(celery_task._result)
        assert result_data.get('error') == 'SEND_FAILED'


class BaseCeleryTaskManagerFailSafeTestCase(TestCase):
    def setUp(self) -> None:
        super().setUp()

        sleep_patcher = patch('django_spire.celery.manager.time.sleep')
        sleep_patcher.start()
        self.addCleanup(sleep_patcher.stop)

    @override_settings(SECRET_KEY=SECRET_KEY)
    @patch('django_spire.celery.manager.send_task')
    def test_creates_failed_record_after_max_retries(self, mock_send_task: MagicMock) -> None:
        from kombu.exceptions import OperationalError as KombuOperationalError

        class MaxRetryManager(BaseCeleryTaskManager):
            task_name = 'max_retry_task'
            display_name = 'Max Retry Task'
            send_task_retries = 2

        mock_send_task.side_effect = KombuOperationalError('Connection failed')

        manager = MaxRetryManager()
        celery_task = manager.send_task()

        assert isinstance(celery_task, CeleryTask)
        assert celery_task.state == states.FAILURE
        result_data = pickle.loads(celery_task._result)
        assert result_data.get('error') == 'SEND_FAILED'

    @override_settings(SECRET_KEY=SECRET_KEY)
    @patch('django_spire.celery.manager.send_task')
    def test_failed_record_contains_error_message(self, mock_send_task: MagicMock) -> None:
        from kombu.exceptions import OperationalError as KombuOperationalError

        mock_send_task.side_effect = KombuOperationalError('RabbitMQ connection refused')

        manager = ManagerTestCeleryTaskManager()
        celery_task = manager.send_task()

        result_data = pickle.loads(celery_task._result)
        assert 'RabbitMQ connection refused' in result_data.get('message')

    @override_settings(SECRET_KEY=SECRET_KEY)
    @patch('django_spire.celery.manager.send_task')
    def test_failed_record_has_send_failed_error_type(self, mock_send_task: MagicMock) -> None:
        from kombu.exceptions import OperationalError as KombuOperationalError

        mock_send_task.side_effect = KombuOperationalError('Failed')

        manager = ManagerTestCeleryTaskManager()
        celery_task = manager.send_task()

        result_data = pickle.loads(celery_task._result)
        assert result_data.get('error') == 'SEND_FAILED'
        assert result_data.get('task_name') == 'test_task'

    @override_settings(SECRET_KEY=SECRET_KEY)
    @patch('django_spire.celery.manager.send_task')
    def test_failed_record_preserves_original_kwargs(self, mock_send_task: MagicMock) -> None:
        from kombu.exceptions import OperationalError as KombuOperationalError

        mock_send_task.side_effect = KombuOperationalError('Failed')

        manager = ManagerTestCeleryTaskManager()
        celery_task = manager.send_task(arg1='value1', arg2='value2', key='value')

        result_data = pickle.loads(celery_task._result)
        assert result_data.get('args') == ()
        assert result_data.get('kwargs') == {'arg1': 'value1', 'arg2': 'value2', 'key': 'value'}

    @override_settings(SECRET_KEY=SECRET_KEY)
    @patch('django_spire.celery.manager.send_task')
    def test_can_distinguish_send_failure_from_task_failure(
        self, mock_send_task: MagicMock
    ) -> None:
        valid_uuid = uuid.uuid4()
        mock_async_result = MagicMock()
        mock_async_result.id = str(valid_uuid)
        mock_send_task.return_value = mock_async_result

        manager = ManagerTestCeleryTaskManager()

        success_task = manager.send_task()
        result_data = pickle.loads(success_task._result)
        error = result_data.get('error') if isinstance(result_data, dict) else None
        assert error != 'SEND_FAILED'

    @override_settings(SECRET_KEY=SECRET_KEY)
    @patch('django_spire.celery.manager.send_task')
    def test_failed_task_result_returns_error_data(self, mock_send_task: MagicMock) -> None:
        from kombu.exceptions import OperationalError as KombuOperationalError

        mock_send_task.side_effect = KombuOperationalError('Connection lost')

        manager = ManagerTestCeleryTaskManager()
        celery_task = manager.send_task(data_id=123)

        result_data = pickle.loads(celery_task._result)
        assert result_data['error'] == 'SEND_FAILED'
        assert result_data['message'] == 'Connection lost'
        assert result_data['kwargs'] == {'data_id': 123}

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
            result_data = pickle.loads(task._result)
            assert result_data.get('error') == 'SEND_FAILED'
