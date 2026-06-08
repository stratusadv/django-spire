from __future__ import annotations

from typing import TYPE_CHECKING

from django_glue import Glue
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.template.response import TemplateResponse
from django.urls import reverse

from django_spire.contrib.session.controller import SessionController
from test_project.app.task.constants import TASK_FILTERING_SESSION_KEY
from test_project.app.task.forms import TaskListFilterForm
from test_project.app.task.models import Task
from test_project.app.task.navigation import TaskNavigation

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


@login_required()
def list_page(request: WSGIRequest):
    nav = TaskNavigation()
    nav.set_page_title_from_model_plural_name(Task)
    nav.breadcrumbs.add_breadcrumb('Task')

    tasks = (
        Task
        .objects
        .active()
        .prefetch_users()
    )

    Glue.model(request, 'task', Task())
    Glue.queryset(request, 'users', User.objects.all())

    context_data = {
        'endpoint': reverse('queryset_filtering:page:list_items'),
        'tasks': tasks,
        'filter_session': SessionController(request, TASK_FILTERING_SESSION_KEY),
        **nav.as_context()
    }

    return TemplateResponse(
        request=request,
        context=context_data,
        template='queryset_filtering/page/list_page.html',
    )


def list_items_view(request: WSGIRequest):
    tasks = (
        Task
        .objects
        .active()
        .prefetch_users()
    )

    context_data = {
        'filter_session': SessionController(request, TASK_FILTERING_SESSION_KEY),
    }

    # return portal_views.infinite_scrolling_view(
    #     request,
    #     context_data=context_data,
    #     queryset=tasks,
    #     queryset_name='tasks',
    #     template='queryset_filtering/item/items.html'
    # )
