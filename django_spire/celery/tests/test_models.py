from __future__ import annotations

import uuid
from datetime import timedelta
from unittest.mock import MagicMock, patch

import pickle
from celery import states
from django.test import TestCase
from django.utils.timezone import now

from django_spire.celery.models import CeleryTask
from django_spire.celery.tests.factories import create_celery_task


class CeleryTaskModelTestCase(TestCase):
    def setUp(self) -> None:
        self.celery_task = create_celery_task()

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

    def test_has_result_false_by_default(self) -> None:
        assert self.celery_task.has_result is False

    def test_result_capture_attempts_zero_by_default(self) -> None:
        assert self.celery_task._result_capture_attempts == 0

    def test_async_result_property(self) -> None:
        result = self.celery_task.async_result
        assert result.id == str(self.celery_task.task_id)

    def test_completion_time_seconds_property(self) -> None:
        started = now() - timedelta(seconds=60)
        completed = now()
        task = create_celery_task(started_datetime=started, completed_datetime=completed)
        assert task.completion_time_seconds == 60

    def test_completion_time_verbose_property(self) -> None:
        started = now() - timedelta(hours=2, minutes=30, seconds=15)
        completed = now()
        task = create_celery_task(started_datetime=started, completed_datetime=completed)
        assert 'hour' in task.completion_time_verbose
        assert 'minute' in task.completion_time_verbose

    def test_estimated_completion_percentage_property(self) -> None:
        started = now() - timedelta(seconds=50)
        estimated = now() + timedelta(seconds=70)
        task = create_celery_task(
            started_datetime=started, estimated_completion_datetime=estimated, state=states.STARTED
        )
        percentage = task.estimated_completion_percentage
        assert 0.0 <= percentage <= 1.0

    def test_estimated_completion_percentage_capped_at_1(self) -> None:
        started = now() - timedelta(seconds=150)
        estimated = now() - timedelta(seconds=10)
        task = create_celery_task(started_datetime=started, estimated_completion_datetime=estimated)
        assert task.estimated_completion_percentage == 1.0

    def test_estimated_completion_percentage_capped_at_0(self) -> None:
        started = now()
        estimated = now() + timedelta(seconds=300)
        task = create_celery_task(started_datetime=started, estimated_completion_datetime=estimated)
        assert task.estimated_completion_percentage >= 0.0

    def test_estimated_completion_percentage_of_hundred(self) -> None:
        task = create_celery_task()
        percentage = task.estimated_completion_percentage_of_hundred
        assert 0 <= percentage <= 100

    def test_estimated_time_remaining_seconds_property(self) -> None:
        estimated = now() + timedelta(seconds=120)
        task = create_celery_task(estimated_completion_datetime=estimated)
        assert 110 <= task.estimated_time_remaining_seconds <= 120

    def test_estimated_time_seconds_property(self) -> None:
        started = now() - timedelta(seconds=30)
        estimated = now() + timedelta(seconds=90)
        task = create_celery_task(started_datetime=started, estimated_completion_datetime=estimated)
        assert 110 <= task.estimated_time_seconds <= 120

    def test_estimated_time_remaining_verbose_property(self) -> None:
        estimated = now() + timedelta(minutes=5, seconds=30)
        task = create_celery_task(estimated_completion_datetime=estimated)
        assert 'minute' in task.estimated_time_remaining_verbose

    def test_is_estimated_complete_soon_true(self) -> None:
        estimated = now() + timedelta(seconds=30)
        task = create_celery_task(estimated_completion_datetime=estimated)
        assert task.is_estimated_complete_soon is True

    def test_is_estimated_complete_soon_false(self) -> None:
        estimated = now() + timedelta(minutes=5)
        task = create_celery_task(estimated_completion_datetime=estimated)
        assert task.is_estimated_complete_soon is False

    def test_is_failed_property(self) -> None:
        task = create_celery_task(state=states.FAILURE)
        assert task.is_failed is True

    def test_is_failed_false(self) -> None:
        task = create_celery_task(state=states.SUCCESS)
        assert task.is_failed is False

    def test_is_successful_property(self) -> None:
        task = create_celery_task(state=states.SUCCESS)
        assert task.is_successful is True

    def test_is_successful_false(self) -> None:
        task = create_celery_task(state=states.PENDING)
        assert task.is_successful is False

    def test_is_processing_property(self) -> None:
        task = create_celery_task(state=states.STARTED)
        assert task.is_processing is True

    def test_is_processing_false(self) -> None:
        task = create_celery_task(state=states.SUCCESS)
        assert task.is_processing is False

    def test_has_no_result_property(self) -> None:
        task = create_celery_task()
        assert task.has_no_result is True
        task.has_result = True
        assert task.has_no_result is False

    def test_result_property_returns_none_when_no_result(self) -> None:
        task = create_celery_task()
        with patch.object(task.services, 'update_result'):
            assert task.result is None

    def test_result_property_returns_pickled_result(self) -> None:
        task = create_celery_task()
        test_data = {'key': 'value', 'number': 42}
        task._result = pickle.dumps(test_data)
        task.has_result = True
        assert task.result == test_data

    def test_result_property_returns_none_on_failure(self) -> None:
        task = create_celery_task(state=states.FAILURE)
        assert task.result is None

    def test_result_setter_pickles_data(self) -> None:
        task = create_celery_task()
        test_data = {'test': 'data'}
        task.result = test_data
        assert pickle.loads(task._result) == test_data

    def test_result_deleter_clears_result(self) -> None:
        task = create_celery_task()
        task._result = pickle.dumps({'test': 'data'})
        del task.result
        assert task._result is None


class CeleryTaskWithModelObjectTestCase(TestCase):
    def test_model_key_generated_from_model_object(self) -> None:
        mock_model = MagicMock()
        mock_model.pk = 123

        task = create_celery_task(model_object=mock_model)
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