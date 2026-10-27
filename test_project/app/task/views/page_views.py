from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse

from test_project.app.task import models
from test_project.app.task.navigation import TaskNavigation

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


@login_required()
def detail_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    task = get_object_or_404(models.Task, pk=pk)

    nav = TaskNavigation()
    nav.page_title = 'Task Details'
    nav.breadcrumbs.add_model_instance_string(task)

    context = nav.as_context()
    context['task'] = task

    return TemplateResponse(request=request, context=context, template='task/page/detail_page.html')
