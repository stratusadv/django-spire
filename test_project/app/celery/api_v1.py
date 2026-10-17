from __future__ import annotations

import json
import uuid
from typing import TYPE_CHECKING

from django.http import HttpResponse, Http404
from ninja import Router, Schema

from django_spire.api.auth.security import ApiKeySecurity
from django_spire.api.choices import ApiPermissionChoices

from django_spire.celery.models import CeleryTask

if TYPE_CHECKING:
    from django.http import HttpRequest

change_auth = ApiKeySecurity(
    api_permission_required=ApiPermissionChoices.CHANGE,
    user_permission_required='django_spire_celery.change_celerytask',
)

router = Router()


class CeleryTaskCancelOut(Schema):
    task_id: str
    state: str


@router.post('tasks/{task_id}/cancel', auth=change_auth, response=CeleryTaskCancelOut)
def cancel_task(
    request: HttpRequest,  # noqa: ARG001
    task_id: str,
) -> CeleryTaskCancelOut | HttpResponse:
    try:
        task_uuid = uuid.UUID(task_id)
    except ValueError:
        raise Http404 from None

    celery_task = CeleryTask.objects.filter(task_id=task_uuid).first()
    if celery_task is None:
        raise Http404

    error = celery_task.services.cancel()
    if error is not None:
        return HttpResponse(
            json.dumps({'error': error}), status=409, content_type='application/json'
        )

    return CeleryTaskCancelOut(task_id=str(celery_task.task_id), state=celery_task.state)
