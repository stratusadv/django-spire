from __future__ import annotations

from typing import TYPE_CHECKING

from celery.result import AsyncResult
from django.contrib.auth.decorators import login_required
from django.template.response import TemplateResponse

from test_project.app.celery.celery.managers import (
    PirateSongCeleryTaskManager,
    NinjaAttackCeleryTaskManager,
)
from test_project.app.celery.models import CeleryStalk
from test_project.app.celery.navigation import CeleryNavigation

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


@login_required
def celery_home_view(request: WSGIRequest) -> TemplateResponse:
    nav = CeleryNavigation()
    nav.page_title = 'Celery Stalking Tasks'
    nav.breadcrumbs.add_breadcrumb('Example')

    template = 'celery/page/home_page.html'

    celery_stalk = CeleryStalk.objects.first()

    context = nav.as_context()

    context['length'] = 5

    if request.method == 'POST':
        length = request.POST.get('length')

        if length is not None:
            length = int(length)

            if request.POST.get('ninja'):
                async_result = NinjaAttackCeleryTaskManager().send_task(length=length)
            else:
                async_result = PirateSongCeleryTaskManager(celery_stalk).send_task(length=length)

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

    context['celery_task_managers'] = [
        NinjaAttackCeleryTaskManager(),
        PirateSongCeleryTaskManager(celery_stalk),
    ]

    return TemplateResponse(request, template, context=context)
