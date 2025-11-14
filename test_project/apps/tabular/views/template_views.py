from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib.auth.models import User
from django.db.models import Count, F, FloatField, Value
from django.db.models.functions import Cast
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse


from test_project.apps.queryset_filtering.constants import TASK_FILTERING_SESSION_KEY
from test_project.apps.queryset_filtering.forms import TaskListFilterForm
from test_project.apps.queryset_filtering.models import Task, TaskUser

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


def tabular_rows_view(request: WSGIRequest) -> TemplateResponse:
    page = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('page_size', 25))
    search = request.GET.get('search', '')
    sort_column = request.GET.get('sort', 'name')
    sort_direction = request.GET.get('direction', 'asc')

    offset = (page - 1) * page_size

    tasks = (
        Task
        .objects
        .active()
        .prefetch_users()
        .search(search)
        .process_session_filter(
            request=request,
            session_key=TASK_FILTERING_SESSION_KEY,
            form_class=TaskListFilterForm,
        )
        .annotate(
            user_count=Count('user'),
            calculated_cost=Cast(F('id') * Value(100), FloatField()),
            calculated_price=Cast(F('id') * Value(150), FloatField())
        )
    )

    sort_mapping = {
        'name': 'name',
        'status': 'status',
        'quantity': 'user_count',
        'cost': 'calculated_cost',
        'date': 'created_datetime',
    }

    sort_field = sort_mapping.get(sort_column, 'created_datetime')
    order_by = f"{'-' if sort_direction == 'desc' else ''}{sort_field}"

    tasks = tasks.order_by(order_by)

    total_count = tasks.count()
    tasks = tasks[offset:offset + page_size]
    has_next = offset + page_size < total_count

    return TemplateResponse(request, 'tabular/table/table_rows.html', {
        'tasks': tasks,
        'has_next': has_next,
    })


def tabular_child_rows_view(request: WSGIRequest, task_id: int) -> TemplateResponse:
    task = get_object_or_404(
        Task.objects.prefetch_related('users', 'users__user'),
        id=task_id
    )

    task_users = task.users.select_related('user').annotate(
        calculated_cost=Cast(Value(50) + F('task_id'), FloatField()),
        calculated_price=Cast(Value(75) + F('task_id'), FloatField())
    )

    return TemplateResponse(request, 'tabular/table/table_child_rows.html', {
        'task': task,
        'task_users': task_users,
    })


def user_details_view(request: WSGIRequest, user_id: int) -> TemplateResponse:
    user = get_object_or_404(User, id=user_id)

    task_users = TaskUser.objects.filter(user=user).select_related('task').annotate(
        calculated_cost=Cast(F('task__id') * Value(100), FloatField()),
    )

    context_data = {
        'user': user,
        'task_users': task_users,
    }

    return TemplateResponse(request, 'tabular/table/user_details.html', context_data)
