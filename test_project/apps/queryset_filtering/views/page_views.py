from django.contrib.messages.context_processors import messages
from django.template.response import TemplateResponse

from test_project.apps.queryset_filtering.models import Task


def list_page(request):
    # We have user input so a form should be used to validate the data.
    filter_form = TaskListFilterForm(request.GET)

    if not filter_form.is_valid():
        # Send error message back to client
        pass


    session = QuerySetFilterSession(request, 'task_list_page') # THis can happen inside process session filter.


    tasks = (
        Task
        .objects
        .active()
        .process_session_filter(request, 'task_list_page', filter_form.cleaned_data) # How do I get the cleaned data or validate the form here?
        .search(request.GET.get('search_value'))
    )


    context_data = {
        'tasks': tasks,
        # 'session_filter_data': request.session.queryset_filtering.get('task_list_page')
    }

    return TemplateResponse(
        request=request,
        context=context_data,
        template='queryset_filtering/page/list_page.html',
    )