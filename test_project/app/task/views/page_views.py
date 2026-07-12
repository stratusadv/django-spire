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
    tasks = models.Task.objects.active().prefetch_users()

    search = request.GET.get('search')
    if search:
        tasks = tasks.search(search)

    paginated_tasks = Paginator(tasks.order_by('name'), 10).get_page(request.GET.get('page', 1))

    Glue.model(request, 'task', models.Task())
    Glue.queryset(request, 'tasks', tasks, Glue.Access.CHANGE)

    nav = TaskNavigation()
    nav.set_page_title_from_model_plural_name(models.Task)

    context = nav.as_context()
    context['tasks'] = paginated_tasks
    context['task_count'] = tasks.count()

    return TemplateResponse(request=request, context=context, template='task/page/list_page.html')


def detail_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    task = get_object_or_404(models.Task, pk=pk)

    nav = TaskNavigation()
    nav.page_title = 'Task Details'
    nav.breadcrumbs.add_model_instance_string(task)

    context = nav.as_context()
    context['task'] = task

    return TemplateResponse(request=request, context=context, template='task/page/detail_page.html')
