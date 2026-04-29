from __future__ import annotations

from typing import TYPE_CHECKING

from celery.result import AsyncResult
from django.contrib.auth.decorators import login_required
from django.template.response import TemplateResponse

from test_project.app.celery.tasks.managers import PirateSongCeleryTaskManager

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


@login_required
def celery_home_view(request: WSGIRequest) -> TemplateResponse:
    template = 'celery/page/home_page.html'

    context = dict()
    context['length'] = 15

    if request.method == 'POST':
        length = request.POST.get('length')

        if length is not None:
            length = int(length)

            async_result = PirateSongCeleryTaskManager().send_task(length)

            context['task_id'] = async_result.id
            context['length'] = length
            context['info'] = 'Your Request has been sent successfully!'

        check_task_id = request.POST.get('check_task_id')

        if check_task_id is not None:
            async_result = AsyncResult(check_task_id)

            context['task_id'] = check_task_id
            context['state'] = async_result.state
            context['celery_task_managers'] = [
                PirateSongCeleryTaskManager()
            ]

            if async_result.state == 'SUCCESS':
                context['result'] = async_result.get(timeout=1)

    return TemplateResponse(
        request,
        template,
        context=context
    )
