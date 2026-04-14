from __future__ import annotations

import uuid
from datetime import timedelta
from unittest.mock import MagicMock, patch

from celery import states
from django.test import TestCase
from django.utils.timezone import now

from django_spire.celery.models import CeleryTask
from django_spire.celery.tests.factories import create_celery_task


class CeleryTaskModelTestCase(TestCase):
    def setUp(self) -> None:
        self.celery_task = create_celery_task()

    def test_str_method(self) -> None:
        expected = f'{self.celery_task.app_name} > {self.celery_task.reference_key}'
        assert str(self.celery_task) == expected

    def test_task_id_field(self) -> None:
        assert self.celery_task.task_id is not None
        assert isinstance(self.celery_task.task_id, str)

    def test_reference_key_field(self) -> None:
        assert self.celery_task.reference_key is not None
        assert len(self.celery_task.reference_key) <= 128

    def test_app_name_field(self) -> None:
        assert self.celery_task.app_name == 'test_project.apps.home'

    def test_reference_name_field(self) -> None:
        assert self.celery_task.reference_name == 'test_task'

    def test_default_state(self) -> None:
        assert self.celery_task.state == states.PENDING

    def test_started_datetime_set(self) -> None:
        assert self.celery_task.started_datetime is not None

    def test_completed_datetime_null_by_default(self) -> None:
        assert self.celery_task.completed_datetime is None

    def test_completed_datetime_set_on_success(self) -> None:
        task = create_celery_task(state=states.SUCCESS)
        assert task.completed_datetime is not None

    def test_async_result_property(self) -> None:
        result = self.celery_task.async_result
        assert result.id == self.celery_task.task_id

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

    def test_reference_name_display_property(self) -> None:
        task = create_celery_task(reference_name='my_test_task')
        assert task.reference_name_display == 'My Test Task'

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


class CeleryTaskReferenceKeyTestCase(TestCase):
    def test_generate_reference_key_with_app_and_reference(self) -> None:
        key = CeleryTask.generate_reference_key(
            app_name='test_app', reference_name='test_reference'
        )
        assert len(key) == 32
        assert isinstance(key, str)

    def test_generate_reference_key_with_model_object(self) -> None:
        mock_model = MagicMock()
        mock_model.__class__.__name__ = 'TestModel'
        mock_model.pk = 123

        key = CeleryTask.generate_reference_key(
            app_name='test_app', reference_name='test_reference', model_object=mock_model
        )
        assert len(key) == 32
        assert 'TestModel' in key or '123' in key

    def test_generate_reference_key_deterministic(self) -> None:
        key1 = CeleryTask.generate_reference_key(
            app_name='test_app', reference_name='test_reference'
        )
        key2 = CeleryTask.generate_reference_key(
            app_name='test_app', reference_name='test_reference'
        )
        assert key1 == key2


class CeleryTaskValidateRegisterArgumentsTestCase(TestCase):
    def test_validate_with_valid_app_name(self) -> None:
        try:
            CeleryTask.validate_register_arguments(
                app_name='django_spire.core', reference_name='valid_reference'
            )
        except Exception:
            assert False, 'validate_register_arguments raised unexpected exception'

    def test_validate_with_invalid_app_name(self) -> None:
        with self.assertRaises(Exception):
            CeleryTask.validate_register_arguments(
                app_name='nonexistent_app', reference_name='valid_reference'
            )

    def test_validate_with_space_in_reference_name(self) -> None:
        with self.assertRaises(ValueError):
            CeleryTask.validate_register_arguments(
                app_name='django_spire.core', reference_name='invalid reference'
            )

    def test_validate_with_hyphen_in_reference_name(self) -> None:
        with self.assertRaises(ValueError):
            CeleryTask.validate_register_arguments(
                app_name='django_spire.core', reference_name='invalid-reference'
            )

    def test_validate_with_underscore_in_reference_name(self) -> None:
        try:
            CeleryTask.validate_register_arguments(
                app_name='django_spire.core', reference_name='valid_reference_name'
            )
        except Exception:
            assert False, 'validate_register_arguments raised unexpected exception'


class CeleryTaskRegisterTestCase(TestCase):
    @patch('django_spire.celery.models.CeleryTask.objects')
    def test_register_creates_task(self, mock_objects) -> None:
        mock_async_result = MagicMock()
        mock_async_result.id = str(uuid.uuid4())

        CeleryTask.register(
            async_result=mock_async_result,
            app_name='django_spire.core',
            reference_name='test_task',
            estimated_completion_seconds=120,
        )

        mock_objects.create.assert_called_once()

    @patch('django_spire.celery.models.CeleryTask.objects')
    def test_register_with_model_object(self, mock_objects) -> None:
        mock_async_result = MagicMock()
        mock_async_result.id = str(uuid.uuid4())
        mock_model = MagicMock()
        mock_model.__class__.__name__ = 'TestModel'
        mock_model.pk = 123

        CeleryTask.register(
            async_result=mock_async_result,
            app_name='django_spire.core',
            reference_name='test_task',
            model_object=mock_model,
        )

        call_args = mock_objects.create.call_args
        assert call_args is not None

    @patch('django_spire.celery.models.CeleryTask.objects')
    def test_register_without_estimated_completion(self, mock_objects) -> None:
        mock_async_result = MagicMock()
        mock_async_result.id = str(uuid.uuid4())

        CeleryTask.register(
            async_result=mock_async_result, app_name='django_spire.core', reference_name='test_task'
        )

        call_args = mock_objects.create.call_args
        assert call_args is not None


class CeleryTaskUpdateFromAsyncResultTestCase(TestCase):
    @patch('django_spire.celery.models.AsyncResult')
    def test_update_from_async_result_changes_state(self, mock_async_result_class) -> None:
        mock_async_result = MagicMock()
        mock_async_result.state = states.SUCCESS
        mock_async_result_class.return_value = mock_async_result

        task = create_celery_task(state=states.PENDING)
        task.update_from_async_result()

        assert task.state == states.SUCCESS

    @patch('django_spire.celery.models.AsyncResult')
    def test_update_from_async_result_sets_completed_datetime(
        self, mock_async_result_class
    ) -> None:
        mock_async_result = MagicMock()
        mock_async_result.state = states.SUCCESS
        mock_async_result_class.return_value = mock_async_result

        task = create_celery_task(state=states.STARTED, completed_datetime=None)
        task.update_from_async_result()

        assert task.completed_datetime is not None

    @patch('django_spire.celery.models.AsyncResult')
    def test_update_from_async_result_does_not_change_completed_on_failure(
        self, mock_async_result_class
    ) -> None:
        mock_async_result = MagicMock()
        mock_async_result.state = states.FAILURE
        mock_async_result_class.return_value = mock_async_result

        completed_before = now() - timedelta(seconds=10)
        task = create_celery_task(state=states.STARTED, completed_datetime=completed_before)
        task.update_from_async_result()

        assert task.completed_datetime == completed_before

    @patch('django_spire.celery.models.AsyncResult')
    def test_update_from_async_result_and_save_saves_changes(self, mock_async_result_class) -> None:
        mock_async_result = MagicMock()
        mock_async_result.state = states.SUCCESS
        mock_async_result_class.return_value = mock_async_result

        task = create_celery_task(state=states.PENDING)
        original_pk = task.pk
        task.update_from_async_result_and_save()

        saved_task = CeleryTask.objects.get(pk=original_pk)
        assert saved_task.state == states.SUCCESS

    @patch('django_spire.celery.models.AsyncResult')
    def test_update_from_async_result_and_save_no_change(self, mock_async_result_class) -> None:
        mock_async_result = MagicMock()
        mock_async_result.state = states.PENDING
        mock_async_result_class.return_value = mock_async_result

        task = create_celery_task(state=states.PENDING)
        original_state = task.state
        task.update_from_async_result_and_save()

        assert task.state == original_state


class CeleryTaskMetaTestCase(TestCase):
    def test_ordering_default(self) -> None:
        assert CeleryTask._meta.ordering == ('-started_datetime',)
