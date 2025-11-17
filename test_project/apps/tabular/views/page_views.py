from __future__ import annotations

import json

from typing import TYPE_CHECKING

from django.contrib.auth.models import User
from django.template.response import TemplateResponse
from django.urls import reverse

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
        .annotate_user_count()
        .annotate_calculated_cost()
        .annotate_calculated_price()
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
        template='tabular/page/list_page.html'
    )


def table_page(request: WSGIRequest):
    Task.objects.process_session_filter(
        request=request,
        session_key=TASK_FILTERING_SESSION_KEY,
        form_class=TaskListFilterForm,
    )

    dg.glue_model_object(request, 'task', Task())
    dg.glue_query_set(request, 'users', User.objects.all())

    context_data = {
        'endpoint': reverse('tabular:template:task_rows'),
        'filter_session': SessionController(request, TASK_FILTERING_SESSION_KEY),
        'status_choices': json.dumps(TaskStatusChoices.choices),
    }

    return TemplateResponse(
        request=request,
        context=context_data,
        template='tabular/page/table_page.html',
    )
