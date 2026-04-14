from celery.result import AsyncResult
from django.db import models

from django_spire.celery.models import CeleryTask


def register_celery_task(
        async_result: AsyncResult,
        app_name: str,
        reference_name: str,
        model_object: models.Model | None = None,
        estimated_completion_seconds: int | None = None,

):
    CeleryTask.register(
        async_result=async_result,
        app_name=app_name,
        reference_name=reference_name,
        model_object=model_object,
        estimated_completion_seconds=estimated_completion_seconds,
    )