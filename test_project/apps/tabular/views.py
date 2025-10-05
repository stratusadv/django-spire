from __future__ import annotations

from typing_extensions import TYPE_CHECKING

from django.template.response import TemplateResponse

from test_project.apps.tabular.context_data import tabular_context_data

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


def tabular_home_view(request: WSGIRequest) -> TemplateResponse:
    context_data = tabular_context_data(page=1, page_size=5)

    context = {
        'rows': context_data['rows'],
        'endpoint': '/tabular/api/rows/',
        'child_endpoint': '/tabular/api/{id}/children/',
        'page_size': 5,
        'current_page': 1,
        'has_next': context_data['has_next'],
        'table_height': '70vh',
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


def tabular_child_rows_view(request: WSGIRequest, task_id: str) -> TemplateResponse:
    all_context = tabular_context_data()

    parent_row = None
    for row in all_context['rows']:
        if str(row['data']['uuid']) == str(task_id):
            parent_row = row
            break

    context = {
        'children': parent_row['child_rows'] if parent_row else [],
    }

    return TemplateResponse(request, 'tabular/table/table_child_rows.html', context=context)
