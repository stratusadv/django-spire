from __future__ import annotations

import hashlib
import pickle
import uuid
from datetime import timedelta

from django.conf import settings
from django.utils.timezone import now

from django_spire.celery.models import CeleryTask
from django_spire.celery.result import CeleryNoResult


def create_test_celery_task(
    task_name: str = 'test_task',
    display_name: str = 'Test Task',
    reference_key: str | None = None,
    model_key: str | None = None,
    task_id: uuid.UUID | str | None = None,
    state: str = 'PENDING',
    started_datetime=None,
    completed_datetime=None,
    estimated_completion_datetime=None,
    has_result: bool = False,
    _result=None,
    model_object=None,
    queued_datetime=None,
) -> CeleryTask:
    if reference_key is None:
        reference_key = f'test_reference_key_{uuid.uuid4().hex[:8]}'

    if task_id is None:
        task_id = uuid.uuid4()
    elif isinstance(task_id, str):
        task_id = uuid.UUID(task_id)

    if started_datetime is None:
        started_datetime = now()

    if queued_datetime is None:
        queued_datetime = started_datetime - timedelta(seconds=1)

    if model_key is None and model_object is not None:
        hashable_string = model_object.__class__.__name__
        hashable_string += str(model_object.pk)
        hashable_string += settings.SECRET_KEY
        model_key = hashlib.md5(hashable_string.encode()).hexdigest()[:128]

    task_meta = {}
    if estimated_completion_datetime:
        task_meta['estimated_completed_time'] = estimated_completion_datetime.timestamp()

    if _result is not None:
        result_value = _result
    elif has_result:
        result_value = pickle.dumps({'test': 'data'})
    else:
        result_value = pickle.dumps(CeleryNoResult())

    return CeleryTask.objects.create(
        task_id=task_id,
        task_name=task_name,
        display_name=display_name,
        reference_key=reference_key,
        model_key=model_key,
        state=state,
        queued_datetime=queued_datetime,
        started_datetime=started_datetime,
        completed_datetime=completed_datetime,
        _task_meta=task_meta or {},
        _result=result_value,
    )
