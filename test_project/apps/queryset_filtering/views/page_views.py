from django.template.response import TemplateResponse

import django_glue as dg

from django_spire.contrib.session.controller import SessionController
from test_project.apps.queryset_filtering.constants import TASK_FILTERING_SESSION_KEY
from test_project.apps.queryset_filtering.models import Task
from test_project.apps.queryset_filtering.forms import TaskListFilterForm


def list_page(request):

    """
        - Enum for actions
        - Tool for queryset filter maps
        - How do we handle glue select field returning false? What should this return?
        - Add Filtering by task users.
    """

    tasks = (
        Task
        .objects
        .active()
        .process_session_filter(
            request=request,
            session_key=TASK_FILTERING_SESSION_KEY,
            form_class=TaskListFilterForm,
        )
    )

    dg.glue_model_object(request, 'task', Task())

    context_data = {
        'tasks': tasks,
        'filter_session': SessionController(request, TASK_FILTERING_SESSION_KEY),
    }

    return TemplateResponse(
        request=request,
        context=context_data,
        template='queryset_filtering/page/list_page.html',
    )