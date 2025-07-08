from django.template.response import TemplateResponse

from django_spire.contrib.form.utils import show_form_errors
from test_project.apps.queryset_filtering.models import Task
from test_project.apps.queryset_filtering.forms import TaskListFilterForm
from test_project.apps.queryset_filtering.views.session import TaskListFilterSession


def list_page(request):
    # We have user input so a form should be used to validate the data.
    filter_form = TaskListFilterForm(request.GET)
    session = TaskListFilterSession(request=request)

    if not filter_form.is_valid():
        show_form_errors(request, filter_form)

    tasks = (
        Task
        .objects
        .active()
        .process_session_filter(
            session=session,
            data=filter_form.cleaned_data
        )
        .search(request.GET.get('search_value'))
    )

    context_data = {
        'tasks': tasks,
        'task_filter_session': session,
        # 'session_filter_data': request.session.queryset_filtering.get('task_list_page')
    }

    return TemplateResponse(
        request=request,
        context=context_data,
        template='queryset_filtering/page/list_page.html',
    )