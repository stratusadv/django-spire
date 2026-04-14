from __future__ import annotations

import uuid
from unittest.mock import MagicMock, patch

from celery.result import AsyncResult
from django.test import TestCase

from django_spire.celery.models import CeleryTask
from django_spire.celery.tools import register_celery_task


class RegisterCeleryTaskTestCase(TestCase):
    @patch('django_spire.celery.tools.CeleryTask')
    def test_register_celery_task_calls_celery_task_register(self, mock_celery_task) -> None:
        mock_async_result = MagicMock(spec=AsyncResult)
        mock_async_result.id = str(uuid.uuid4())

        register_celery_task(
            async_result=mock_async_result, app_name='django_spire.core', reference_name='test_task'
        )

        mock_celery_task.register.assert_called_once_with(
            async_result=mock_async_result,
            app_name='django_spire.core',
            reference_name='test_task',
            model_object=None,
            estimated_completion_seconds=None,
        )

    @patch('django_spire.celery.tools.CeleryTask')
    def test_register_celery_task_with_model_object(self, mock_celery_task) -> None:
        mock_async_result = MagicMock(spec=AsyncResult)
        mock_async_result.id = str(uuid.uuid4())
        mock_model = MagicMock()

        register_celery_task(
            async_result=mock_async_result,
            app_name='django_spire.core',
            reference_name='test_task',
            model_object=mock_model,
        )

        mock_celery_task.register.assert_called_once_with(
            async_result=mock_async_result,
            app_name='django_spire.core',
            reference_name='test_task',
            model_object=mock_model,
            estimated_completion_seconds=None,
        )

    @patch('django_spire.celery.tools.CeleryTask')
    def test_register_celery_task_with_estimated_completion(self, mock_celery_task) -> None:
        mock_async_result = MagicMock(spec=AsyncResult)
        mock_async_result.id = str(uuid.uuid4())

        register_celery_task(
            async_result=mock_async_result,
            app_name='django_spire.core',
            reference_name='test_task',
            estimated_completion_seconds=120,
        )

        mock_celery_task.register.assert_called_once_with(
            async_result=mock_async_result,
            app_name='django_spire.core',
            reference_name='test_task',
            model_object=None,
            estimated_completion_seconds=120,
        )

    @patch('django_spire.celery.tools.CeleryTask')
    def test_register_celery_task_with_all_parameters(self, mock_celery_task) -> None:
        mock_async_result = MagicMock(spec=AsyncResult)
        mock_async_result.id = str(uuid.uuid4())
        mock_model = MagicMock()

        register_celery_task(
            async_result=mock_async_result,
            app_name='django_spire.core',
            reference_name='test_task',
            model_object=mock_model,
            estimated_completion_seconds=300,
        )

        mock_celery_task.register.assert_called_once_with(
            async_result=mock_async_result,
            app_name='django_spire.core',
            reference_name='test_task',
            model_object=mock_model,
            estimated_completion_seconds=300,
        )
