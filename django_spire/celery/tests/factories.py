from __future__ import annotations

import uuid
from datetime import timedelta

from celery.result import AsyncResult
from django.utils.timezone import now

from django_spire.celery.models import CeleryTask


def create_celery_task(
    app_name: str = 'test_project.apps.home',
    reference_name: str = 'test_task',
    reference_key: str | None = None,
    task_id: str | None = None,
    state: str = 'PENDING',
    started_datetime=None,
    completed_datetime=None,
    estimated_completion_datetime=None,
    model_object=None,
) -> CeleryTask:
    if reference_key is None:
        reference_key = CeleryTask.generate_reference_key(
            app_name=app_name, reference_name=reference_name, model_object=model_object
        )

    if task_id is None:
        task_id = str(uuid.uuid4())

    if started_datetime is None:
        started_datetime = now()

    if estimated_completion_datetime is None:
        estimated_completion_datetime = started_datetime + timedelta(seconds=120)

    return CeleryTask.objects.create(
        task_id=task_id,
        reference_key=reference_key,
        app_name=app_name,
        reference_name=reference_name,
        state=state,
        started_datetime=started_datetime,
        completed_datetime=completed_datetime,
        estimated_completion_datetime=estimated_completion_datetime,
    )


def create_mock_async_result(task_id: str | None = None, state: str = 'PENDING') -> AsyncResult:
    if task_id is None:
        task_id = str(uuid.uuid4())

    mock_result = AsyncResult(task_id)
    mock_result.state = state

    return mock_result
