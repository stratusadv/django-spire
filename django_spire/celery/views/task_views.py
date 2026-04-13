from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse

from django_spire.celery.models import CeleryTask

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


@login_required
def task_view(request: WSGIRequest, task_id: str) -> TemplateResponse:
    template = 'django_spire/celery/toast/task_toast.html'

    celery_task = get_object_or_404(CeleryTask, task_id=task_id)

    celery_task.update_from_async_result_and_save()

    context = {
        'celery_task': celery_task
    }

    return TemplateResponse(
        request,
        template,
        context=context
    )


@login_required
def task_list_view(request: WSGIRequest, reference_key: str) -> TemplateResponse:
    template = 'django_spire/celery/toast/task_toast_list.html'

    celery_tasks = CeleryTask.objects.by_reference_key(reference_key).by_unready()

    context = {
        'celery_tasks': celery_tasks
    }

    return TemplateResponse(
        request,
        template,
        context=context
    )
