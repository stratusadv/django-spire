from __future__ import annotations

from typing import TYPE_CHECKING

from django_spire.contrib.generic_views.portal_views import infinite_scrolling_view

from test_project.apps.infinite_scrolling.constants import INFINITE_SCROLLING_FILTERING_SESSION_KEY
from test_project.apps.infinite_scrolling.forms import InfiniteScrollingListFilterForm
from test_project.apps.infinite_scrolling.models import InfiniteScrolling

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest
    from django.template.response import TemplateResponse


def items_view(request: WSGIRequest) -> TemplateResponse:
    infinite_scrollings = (
        InfiniteScrolling
        .objects
        .active()
        .process_session_filter(
            request=request,
            session_key=INFINITE_SCROLLING_FILTERING_SESSION_KEY,
            form_class=InfiniteScrollingListFilterForm,
        )
        .order_by('-created_datetime')
    )

    context_data = {
        'batch_size': 10,
    }

    return infinite_scrolling_view(
        request,
        context_data=context_data,
        queryset=infinite_scrollings,
        queryset_name='infinite_scrollings',
        template='infinite_scrolling/item/items.html'
    )


def rows_view(request: WSGIRequest) -> TemplateResponse:
    sort_column = request.GET.get('sort', 'name')
    sort_direction = request.GET.get('direction', 'asc')

    infinite_scrollings = (
        InfiniteScrolling
        .objects
        .active()
        .process_session_filter(
            request=request,
            session_key=INFINITE_SCROLLING_FILTERING_SESSION_KEY,
            form_class=InfiniteScrollingListFilterForm,
        )
    )

    sort_mapping = {
        'created': 'created_datetime',
        'description': 'description',
        'name': 'name',
    }

    sort_field = sort_mapping.get(sort_column, 'name')
    order_by = f"{'-' if sort_direction == 'desc' else ''}{sort_field}"

    infinite_scrollings = infinite_scrollings.order_by(order_by)

    context_data = {
        'batch_size': 20,
    }

    return infinite_scrolling_view(
        request,
        context_data=context_data,
        queryset=infinite_scrollings,
        queryset_name='infinite_scrollings',
        template='infinite_scrolling/table/rows.html'
    )
