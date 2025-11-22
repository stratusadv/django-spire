from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib.auth.models import User
from django.db.migrations.recorder import MigrationRecorder
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse

from django_spire.contrib.generic_views.portal_views import table_view

from test_project.apps.queryset_filtering.constants import TASK_FILTERING_SESSION_KEY
from test_project.apps.queryset_filtering.forms import TaskListFilterForm
from test_project.apps.queryset_filtering.models import Task, TaskUser

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


def migration_rows_view(request: WSGIRequest) -> TemplateResponse:
    sort_column = request.GET.get('sort', 'applied')
    sort_direction = request.GET.get('direction', 'desc')

    migrations = MigrationRecorder.Migration.objects.all()

    sort_mapping = {
        'app': 'app',
        'name': 'name',
        'applied': 'applied',
    }

    sort_field = sort_mapping.get(sort_column, 'applied')
    order_by = f"{'-' if sort_direction == 'desc' else ''}{sort_field}"

    migrations = migrations.order_by(order_by)

    return table_view(
        request,
        queryset=migrations,
        queryset_name='migrations',
        template='tabular/table/migration_rows.html'
    )


def detail_rows_view(request: WSGIRequest, task_id: int) -> TemplateResponse:
    task = get_object_or_404(Task, id=task_id)

    context_data = {
        'task': task,
    }

    return TemplateResponse(
        request,
        context=context_data,
        template='tabular/table/detail_rows.html'
    )


def rows_view(request: WSGIRequest) -> TemplateResponse:
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

    context_data = {'batch_size': 10}

    return table_view(
        request,
        context_data=context_data,
        queryset=tasks,
        queryset_name='tasks',
        template='tabular/table/rows.html'
    )


def user_detail_rows_view(request: WSGIRequest, user_id: int) -> TemplateResponse:
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
        template='tabular/table/user_detail_rows.html'
    )


def user_rows_view(request: WSGIRequest, task_id: int) -> TemplateResponse:
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
        template='tabular/table/user_rows.html'
    )
