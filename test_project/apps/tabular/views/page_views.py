from __future__ import annotations

import json

from typing import TYPE_CHECKING

from django.contrib.auth.models import User
from django.db.models import Count, F, FloatField, Value
from django.db.models.functions import Cast
from django.template.response import TemplateResponse

import django_glue as dg

from django_spire.contrib.session.controller import SessionController

from test_project.apps.queryset_filtering.choices import TaskStatusChoices
from test_project.apps.queryset_filtering.constants import TASK_FILTERING_SESSION_KEY
from test_project.apps.queryset_filtering.forms import TaskListFilterForm
from test_project.apps.queryset_filtering.models import Task

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


def list_page(request: WSGIRequest):
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
        .annotate(
            user_count=Count('user'),
            calculated_cost=Cast(F('id') * Value(100), FloatField()),
            calculated_price=Cast(F('id') * Value(150), FloatField())
        )
        .order_by('-created_datetime')
    )

    dg.glue_model_object(request, 'task', Task())
    dg.glue_query_set(request, 'users', User.objects.all())

    context_data = {
        'tasks': tasks,
        'filter_session': SessionController(request, TASK_FILTERING_SESSION_KEY),
    }

    return TemplateResponse(
        request=request,
        context=context_data,
        template='tabular/page/list_page.html',
    )


def table_page(request: WSGIRequest):
    page_size = 25

    total_count = (
        Task
        .objects
        .active()
        .prefetch_users()
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
        .count()
    )

    dg.glue_model_object(request, 'task', Task())
    dg.glue_query_set(request, 'users', User.objects.all())

    context_data = {
        'tasks': [],
        'endpoint': '/tabular/template/api/rows/',
        'child_endpoint': '/tabular/template/api/{id}/children/',
        'page_size': page_size,
        'current_page': 0,
        'has_next': True,
        'total_count': total_count,
        'filter_session': SessionController(request, TASK_FILTERING_SESSION_KEY),
        'status_choices': json.dumps(TaskStatusChoices.choices),
    }

    return TemplateResponse(
        request=request,
        context=context_data,
        template='tabular/page/table_page.html',
    )
