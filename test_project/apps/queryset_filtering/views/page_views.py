from django.template.response import TemplateResponse

from test_project.apps.queryset_filtering.models import Task


def list_page(request):

    tasks = (
        Task
        .objects
        .active()
        .process_session_filter(request, 'task_list_page')
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