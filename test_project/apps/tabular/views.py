from __future__ import annotations

from typing_extensions import TYPE_CHECKING

from django.template.response import TemplateResponse

from test_project.apps.tabular.context_data import tabular_context_data
from test_project.apps.queryset_filtering.models import Task

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


def tabular_home_view(request: WSGIRequest) -> TemplateResponse:
    page_size = 25

    context_data = tabular_context_data(page=1, page_size=page_size)

    context = {
        'rows': [],
        'endpoint': '/tabular/api/rows/',
        'child_endpoint': '/tabular/api/{id}/children/',
        'page_size': page_size,
        'current_page': 0,
        'has_next': True,
        'total_count': context_data['total_count'],
    }

    return TemplateResponse(request, 'tabular/page/tabular_home_page.html', context=context)


def tabular_rows_view(request: WSGIRequest) -> TemplateResponse:
    page = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('page_size', 5))
    search = request.GET.get('search', '')
    sort_column = request.GET.get('sort', 'name')
    sort_direction = request.GET.get('direction', 'asc')

    context_data = tabular_context_data(
        page=page,
        page_size=page_size,
        search=search,
        sort_column=sort_column,
        sort_direction=sort_direction
    )

    return TemplateResponse(request, 'tabular/table/table_rows.html', {
        'rows': context_data['rows'],
        'has_next': context_data['has_next'],
    })


def tabular_child_rows_view(request: WSGIRequest, task_id: int) -> TemplateResponse:
    try:
        task = Task.objects.prefetch_related('users', 'users__user').get(id=task_id)

        children = []
        for task_user in task.users.all():
            child_row = {
                'child_data': {
                    'uuid': f"task-{task.id}-user-{task_user.user.id}",
                    'quantity': 1,
                    'cost': float(50 + task.id),
                    'price': float(75 + task.id),
                    'date': task_user.created_datetime.date(),
                    'user_name': task_user.user.get_full_name() or task_user.user.username,
                    'role': task_user.get_role_display(),
                }
            }
            children.append(child_row)

        context = {
            'children': children,
        }

    except Task.DoesNotExist:
        context = {
            'children': [],
            'error': 'Task not found'
        }

    return TemplateResponse(request, 'tabular/table/table_child_rows.html', context=context)
