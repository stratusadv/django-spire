from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse

from django_spire.contrib.generic_views.portal_views import table_view

from test_project.apps.queryset_filtering.constants import TASK_FILTERING_SESSION_KEY
from test_project.apps.queryset_filtering.forms import TaskListFilterForm
from test_project.apps.queryset_filtering.models import Task, TaskUser

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


def tabular_rows_view(request: WSGIRequest) -> TemplateResponse:
    sort_column = request.GET.get('sort', 'name')
    sort_direction = request.GET.get('direction', 'asc')

    tasks = (
        Task
        .objects
        .active()
        .prefetch_users()
        .process_session_filter(
            request=request,
            session_key=TASK_FILTERING_SESSION_KEY,
            form_class=TaskListFilterForm,
        )
        .annotate_user_count()
        .annotate_calculated_cost()
        .annotate_calculated_price()
        .sort_by_column(sort_column, sort_direction)
    )

    return table_view(
        request,
        queryset=tasks,
        queryset_name='tasks',
        template='tabular/table/rows.html'
    )


def tabular_child_rows_view(request: WSGIRequest, task_id: int) -> TemplateResponse:
    task = get_object_or_404(
        Task.objects.prefetch_related('users', 'users__user'),
        id=task_id
    )

    task_users = (
        task
        .users
        .select_related('user')
        .annotate_calculated_cost()
        .annotate_calculated_price()
    )

    context_data = {
        'task': task,
        'task_users': task_users,
    }

    return TemplateResponse(
        request,
        context=context_data,
        template='tabular/table/child_rows.html'
    )


def user_details_view(request: WSGIRequest, user_id: int) -> TemplateResponse:
    user = get_object_or_404(User, id=user_id)

    task_users = (
        TaskUser
        .objects
        .filter(user=user)
        .select_related('task')
        .annotate_user_cost()
    )

    context_data = {
        'user': user,
        'task_users': task_users,
    }

    return TemplateResponse(
        request,
        context=context_data,
        template='tabular/table/user_details.html'
    )
