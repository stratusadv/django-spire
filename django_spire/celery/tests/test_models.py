from __future__ import annotations

import pickle
import uuid
from datetime import timedelta
from unittest.mock import MagicMock

from celery import states
from django.test import TestCase
from django.utils.timezone import now

from django_spire.celery.models import CeleryTask
from django_spire.celery.tests.factories import create_test_celery_task
from django_spire.celery.result import CeleryNoResult


class CeleryTaskModelTestCase(TestCase):
    def setUp(self) -> None:
        self.celery_task = create_test_celery_task()

    def test_str_method(self) -> None:
        assert str(self.celery_task) == f'{self.celery_task.task_name}'

    def test_task_id_field(self) -> None:
        assert self.celery_task.task_id is not None
        assert isinstance(self.celery_task.task_id, uuid.UUID)

    def test_reference_key_field(self) -> None:
        assert self.celery_task.reference_key is not None
        assert len(self.celery_task.reference_key) <= 128

    def test_task_name_field(self) -> None:
        assert self.celery_task.task_name is not None

    def test_display_name_field(self) -> None:
        assert self.celery_task.display_name is not None

    def test_model_key_field_null_by_default(self) -> None:
        assert self.celery_task.model_key is None

    def test_default_state(self) -> None:
        assert self.celery_task.state == states.PENDING

    def test_started_datetime_set(self) -> None:
        assert self.celery_task.started_datetime is not None

    def test_completed_datetime_null_by_default(self) -> None:
        assert self.celery_task.completed_datetime is None

    def test_result_capture_attempts_zero_by_default(self) -> None:
        assert self.celery_task._result_capture_attempts == 0

    def test_async_result_property(self) -> None:
        result = self.celery_task.async_result
        assert result.id == str(self.celery_task.task_id)

    def test_completion_time_seconds_property(self) -> None:
        started = now() - timedelta(seconds=60)
        completed = now()
        task = create_test_celery_task(started_datetime=started, completed_datetime=completed)
        assert 59 <= task.completion_time_seconds <= 61

    def test_completion_time_verbose_property(self) -> None:
        started = now() - timedelta(hours=2, minutes=30, seconds=15)
        completed = now()
        task = create_test_celery_task(started_datetime=started, completed_datetime=completed)
        assert 'hour' in task.completion_time_verbose
        assert 'minute' in task.completion_time_verbose

    def test_result_setter_pickles_data(self) -> None:
        task = create_test_celery_task()
        test_data = {'test': 'data'}
        task.result = test_data
        assert pickle.loads(task._result) == test_data

    def test_result_deleter_clears_result(self) -> None:
        task = create_test_celery_task()
        task._result = pickle.dumps({'test': 'data'})
        del task.result
        assert task._result is None

    def test_is_failed_property(self) -> None:
        task = create_test_celery_task(state=states.FAILURE)
        assert task.is_failed is True

    def test_is_failed_false(self) -> None:
        task = create_test_celery_task(state=states.SUCCESS)
        assert task.is_failed is False

    def test_is_successful_property(self) -> None:
        task = create_test_celery_task(state=states.SUCCESS)
        assert task.is_successful is True

    def test_is_successful_false(self) -> None:
        task = create_test_celery_task(state=states.PENDING)
        assert task.is_successful is False

    def test_is_processing_property(self) -> None:
        task = create_test_celery_task(state=states.STARTED)
        assert task.is_processing is True

    def test_is_processing_false(self) -> None:
        task = create_test_celery_task(state=states.SUCCESS)
        assert task.is_processing is False

    def test_is_pending_property(self) -> None:
        task = create_test_celery_task(state=states.PENDING)
        assert task.is_pending is True


class CeleryTaskWithModelObjectTestCase(TestCase):
    def test_model_key_generated_from_model_object(self) -> None:
        mock_model = MagicMock()
        mock_model.pk = 123

        task = create_test_celery_task(model_object=mock_model)
        assert task.model_key is not None
        assert len(task.model_key) <= 128


class CeleryTaskMetaTestCase(TestCase):
    def test_ordering_default(self) -> None:
        assert CeleryTask._meta.ordering == ('-started_datetime',)

    def test_verbose_name(self) -> None:
        assert CeleryTask._meta.verbose_name == 'Celery Task'

    def test_verbose_name_plural(self) -> None:
        assert CeleryTask._meta.verbose_name_plural == 'Celery Tasks'

    def test_db_table(self) -> None:
        assert CeleryTask._meta.db_table == 'django_spire_celery_task'


class CeleryTaskSendFailedPropertiesTestCase(TestCase):
    def test_send_failed_false_when_no_result(self) -> None:
        task = create_test_celery_task()
        task._result = pickle.dumps(CeleryNoResult())
        task.save()
        result_data = pickle.loads(task._result)
        assert isinstance(result_data, CeleryNoResult)

    def test_send_failed_false_when_result_is_not_send_failed(self) -> None:
        task = create_test_celery_task()
        task._result = pickle.dumps({'data': 'value'})
        task.save()
        result_data = pickle.loads(task._result)
        assert result_data.get('error') != 'SEND_FAILED'

    def test_send_failed_true_when_result_is_send_failed(self) -> None:
        task = create_test_celery_task()
        task._result = pickle.dumps(
            {
                'error': 'SEND_FAILED',
                'message': 'Connection refused',
                'args': (),
                'kwargs': {},
                'task_name': 'test_task',
            }
        )
        task.save()
        result_data = pickle.loads(task._result)
        assert result_data.get('error') == 'SEND_FAILED'

    def test_send_error_message_returns_none_when_not_failed(self) -> None:
        task = create_test_celery_task()
        task._result = pickle.dumps({'data': 'value'})
        task.save()
        result_data = pickle.loads(task._result)
        assert result_data.get('error') != 'SEND_FAILED'

    def test_send_error_message_returns_message_on_failure(self) -> None:
        task = create_test_celery_task()
        task._result = pickle.dumps(
            {
                'error': 'SEND_FAILED',
                'message': 'RabbitMQ unavailable',
                'args': ('arg1',),
                'kwargs': {'key': 'value'},
                'task_name': 'my_task',
            }
        )
        task.save()
        result_data = pickle.loads(task._result)
        assert result_data.get('message') == 'RabbitMQ unavailable'

    def test_send_error_details_returns_none_when_not_failed(self) -> None:
        task = create_test_celery_task()
        task._result = pickle.dumps({'data': 'value'})
        task.save()
        result_data = pickle.loads(task._result)
        assert result_data.get('error') != 'SEND_FAILED'

    def test_send_error_details_returns_full_error_data(self) -> None:
        task = create_test_celery_task()
        task._result = pickle.dumps(
            {
                'error': 'SEND_FAILED',
                'message': 'Connection lost',
                'args': ('arg1', 'arg2'),
                'kwargs': {'key': 'value'},
                'task_name': 'my_task',
            }
        )
        task.save()
        result_data = pickle.loads(task._result)
        assert result_data['task_name'] == 'my_task'
        assert result_data['args'] == ('arg1', 'arg2')
        assert result_data['kwargs'] == {'key': 'value'}
        assert result_data['message'] == 'Connection lost'

    def test_failed_task_result_contains_error_data(self) -> None:
        task = create_test_celery_task()
        task._result = pickle.dumps(
            {
                'error': 'SEND_FAILED',
                'message': 'Failed',
                'args': (),
                'kwargs': {},
                'task_name': 'test',
            }
        )
        task.save()
        result_data = pickle.loads(task._result)
        assert result_data['error'] == 'SEND_FAILED'
