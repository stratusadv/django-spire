from django.template.response import TemplateResponse

from test_project.apps.queryset_filtering.models import Task


def list_page(request):
    context_data = {
        'tasks': Task.objects.active()
    }

    return TemplateResponse(
        request=request,
        context=context_data,
        template='queryset_filtering/page/list_page.html',
    )