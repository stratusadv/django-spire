from django.template.response import TemplateResponse

from django_spire.core.filtering.filters import QuerySetFilter
from test_project.apps.queryset_filtering.models import Task


def list_page(request):
    queryset_filter = QuerySetFilter(request, filter_key='task_queryset_filter')
    tasks = queryset_filter.process_queryset(Task.objects.all())

    context_data = {
        'tasks': Task.objects.active(),
        'queryset_filter': queryset_filter,
    }

    return TemplateResponse(
        request=request,
        context=context_data,
        template='queryset_filtering/page/list_page.html',
    )