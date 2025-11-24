from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib.auth.models import User
from django.template.response import TemplateResponse
from django.urls import reverse

import django_glue as dg

from django_spire.contrib.generic_views import portal_views
from django_spire.contrib.session.controller import SessionController

from test_project.apps.queryset_filtering.constants import TASK_FILTERING_SESSION_KEY
from test_project.apps.queryset_filtering.models import Task
from test_project.apps.queryset_filtering.forms import TaskListFilterForm

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


def list_page(request: WSGIRequest):

    """
        - Test glue multi select field in other projects.
        - Review Code
        - Update docs
    """

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
    )

    dg.glue_model_object(request, 'task', Task())
    dg.glue_query_set(request, 'users', User.objects.all())

    context_data = {
        'endpoint': reverse('queryset_filtering:page:list_items'),
        'tasks': tasks,
        'filter_session': SessionController(request, TASK_FILTERING_SESSION_KEY),
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
        .process_session_filter(
            request=request,
            session_key=TASK_FILTERING_SESSION_KEY,
            form_class=TaskListFilterForm,
        )
    )

    context_data = {
        'filter_session': SessionController(request, TASK_FILTERING_SESSION_KEY),
    }

    return portal_views.infinite_scrolling_view(
        request,
        context_data=context_data,
        queryset=tasks,
        queryset_name='tasks',
        template='queryset_filtering/item/items.html'
    )
