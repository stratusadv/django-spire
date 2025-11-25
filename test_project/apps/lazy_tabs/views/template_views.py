from __future__ import annotations

from typing import TYPE_CHECKING

from django.template.response import TemplateResponse
from django.urls import reverse

from django_spire.contrib.generic_views.portal_views import infinite_scrolling_view

from test_project.apps.lazy_tabs.models import LazyTabs

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


def tab_overview_view(request: WSGIRequest) -> TemplateResponse:
    context_data = {}

    return TemplateResponse(
        request=request,
        context=context_data,
        template='lazy_tabs/tab/overview.html',
    )


def tab_details_view(request: WSGIRequest) -> TemplateResponse:
    context_data = {}

    return TemplateResponse(
        request=request,
        context=context_data,
        template='lazy_tabs/tab/details.html',
    )


def tab_settings_view(request: WSGIRequest) -> TemplateResponse:
    context_data = {}

    return TemplateResponse(
        request=request,
        context=context_data,
        template='lazy_tabs/tab/settings.html',
    )


def tab_profile_view(request: WSGIRequest) -> TemplateResponse:
    context_data = {}

    return TemplateResponse(
        request=request,
        context=context_data,
        template='lazy_tabs/tab/profile.html',
    )


def tab_activity_view(request: WSGIRequest) -> TemplateResponse:
    context_data = {}

    return TemplateResponse(
        request=request,
        context=context_data,
        template='lazy_tabs/tab/activity.html',
    )


def tab_items_view(request: WSGIRequest) -> TemplateResponse:
    context_data = {
        'endpoint': reverse('lazy_tabs:template:items'),
    }

    return TemplateResponse(
        request=request,
        context=context_data,
        template='lazy_tabs/tab/items.html',
    )


def tab_table_view(request: WSGIRequest) -> TemplateResponse:
    context_data = {
        'endpoint': reverse('lazy_tabs:template:rows'),
    }

    return TemplateResponse(
        request=request,
        context=context_data,
        template='lazy_tabs/tab/table.html',
    )


def items_view(request: WSGIRequest) -> TemplateResponse:
    lazy_tabs = (
        LazyTabs
        .objects
        .active()
        .order_by('-created_datetime')
    )

    context_data = {
        'batch_size': 10,
    }

    return infinite_scrolling_view(
        request,
        context_data=context_data,
        queryset=lazy_tabs,
        queryset_name='lazy_tabs_items',
        template='lazy_tabs/item/items.html'
    )


def rows_view(request: WSGIRequest) -> TemplateResponse:
    sort_column = request.GET.get('sort', 'name')
    sort_direction = request.GET.get('direction', 'asc')

    lazy_tabs = LazyTabs.objects.active()

    sort_mapping = {
        'created': 'created_datetime',
        'description': 'description',
        'name': 'name',
    }

    sort_field = sort_mapping.get(sort_column, 'name')
    order_by = f"{'-' if sort_direction == 'desc' else ''}{sort_field}"

    lazy_tabs = lazy_tabs.order_by(order_by)

    context_data = {
        'batch_size': 20,
    }

    return infinite_scrolling_view(
        request,
        context_data=context_data,
        queryset=lazy_tabs,
        queryset_name='lazy_tabs_items',
        template='lazy_tabs/table/rows.html'
    )
