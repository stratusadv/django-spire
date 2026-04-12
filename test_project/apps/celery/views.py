from __future__ import annotations

import datetime
from datetime import timedelta
from typing import TYPE_CHECKING

from celery.result import AsyncResult
from django.template.response import TemplateResponse

from django_spire.celery.models import CeleryTask
from test_project.apps.celery.tasks import pirate_noise_task

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


def celery_home_view(request: WSGIRequest) -> TemplateResponse:
    template = 'celery/page/home_page.html'

    context = dict()
    context['length'] = 15

    if request.method == 'POST':
        length = request.POST.get('length')

        if length is not None:
            length = int(length)

            async_result = pirate_noise_task.apply_async(
                (length,),
                eta=datetime.datetime.now() + timedelta(seconds=length+2),
            )

            CeleryTask.register(
                async_result=async_result,
                app_label='test_project_celery',
                reference_name='pirate_noise_task',
            )

            context['task_id'] = async_result.id
            context['length'] = length
            context['info'] = 'Your Request has been sent successfully!'

        check_task_id = request.POST.get('check_task_id')

        if check_task_id is not None:
            async_result = AsyncResult(check_task_id)

            context['task_id'] = check_task_id
            context['state'] = async_result.state

            if async_result.state == 'SUCCESS':
                context['result'] = async_result.get(timeout=1)

    return TemplateResponse(
        request,
        template,
        context=context
    )
