from __future__ import annotations

import json

from docutils.nodes import reference

from typing import TYPE_CHECKING

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse

from django_spire.celery.models import CeleryTask

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


@login_required
def _task_view(request: WSGIRequest, template: str, task_id: str) -> TemplateResponse:
    celery_task = get_object_or_404(CeleryTask, task_id=task_id)

    celery_task.services.update_from_async_result_and_save_if_change()

    context = {'celery_task': celery_task}

    return TemplateResponse(request, template, context=context)


@login_required
def task_item_view(request: WSGIRequest, task_id: str) -> TemplateResponse:
    template = 'django_spire/celery/item/task_item.html'
    return _task_view(request, template, task_id)


@login_required
def task_toast_view(request: WSGIRequest, task_id: str) -> TemplateResponse:
    template = 'django_spire/celery/toast/task_toast.html'
    return _task_view(request, template, task_id)


@login_required
def _list_view(
    request: WSGIRequest, template: str, django_spire_celery_task_key_pairs: str
) -> TemplateResponse:
    reference_keys_model_keys = {}

    for key_pair in django_spire_celery_task_key_pairs.split(','):
        keys = key_pair.split('|')
        reference_keys_model_keys[keys[0]] = keys[1] if len(keys) == 2 else None

    celery_tasks = CeleryTask.objects.by_reference_keys_model_keys(
        reference_keys_model_keys
    )

    if not request.GET.get('show_all', False):
        celery_tasks = celery_tasks.by_unready()

    context = {'celery_tasks': celery_tasks}

    return TemplateResponse(request, template, context=context)


@login_required
def task_item_list_view(request: WSGIRequest) -> TemplateResponse:
    data = json.loads(request.body)
    django_spire_celery_task_key_pairs = data.get(
        'django_spire_celery_task_key_pairs'
    )
    template = 'django_spire/celery/item/task_item_list.html'
    return _list_view(request, template, django_spire_celery_task_key_pairs)


@login_required
def task_toast_list_view(request: WSGIRequest) -> TemplateResponse:
    data = json.loads(request.body)
    django_spire_celery_task_key_pairs = data.get(
        'django_spire_celery_task_key_pairs'
    )
    template = 'django_spire/celery/toast/task_toast_list.html'
    return _list_view(request, template, django_spire_celery_task_key_pairs)
