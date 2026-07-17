from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.urls import reverse
from django_glue import Glue

from test_project.app.task import models
from test_project.app.task.navigation import TaskNavigation

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


@login_required()
def list_view(request: WSGIRequest) -> TemplateResponse:
    # REMOVE SLICING AFTER GLUE IS FIXED
    tasks = models.Task.objects.active().top_level().prefetch_users()
    child_tasks = models.Task.objects.active().children().prefetch_users()

    Glue.queryset(request, 'tasks', tasks, Glue.Access.CHANGE)
    Glue.queryset(request, 'child_tasks', child_tasks, Glue.Access.CHANGE)

    nav = TaskNavigation()
    nav.set_page_title_from_model_plural_name(models.Task)

    context = nav.as_context()
    context['task_count'] = tasks.count()

    return TemplateResponse(request=request, context=context, template='task/page/list_page.html')


@login_required()
def detail_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    task = get_object_or_404(models.Task, pk=pk)

    nav = TaskNavigation()
    nav.page_title = 'Task Details'
    nav.breadcrumbs.add_model_instance_string(task)

    context = nav.as_context()
    context['task'] = task

    return TemplateResponse(request=request, context=context, template='task/page/detail_page.html')
