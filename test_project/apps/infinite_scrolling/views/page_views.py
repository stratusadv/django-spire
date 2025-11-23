from __future__ import annotations

from typing import TYPE_CHECKING

from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.urls import reverse

import django_glue as dg

from django_spire.contrib.generic_views import portal_views
from django_spire.contrib.session.controller import SessionController
from django_spire.core.shortcuts import get_object_or_null_obj

from test_project.apps.infinite_scrolling.constants import INFINITE_SCROLLING_FILTERING_SESSION_KEY
from test_project.apps.infinite_scrolling.forms import InfiniteScrollingListFilterForm
from test_project.apps.infinite_scrolling.models import InfiniteScrolling

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


def cards_page_view(request: WSGIRequest) -> TemplateResponse:
    context_data = {
        'endpoint': reverse('infinite_scrolling:template:items'),
    }

    return TemplateResponse(
        request=request,
        context=context_data,
        template='infinite_scrolling/page/cards_page.html',
    )


def delete_page_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    infinite_scrolling = get_object_or_404(InfiniteScrolling, pk=pk)

    return_url = request.GET.get(
        'return_url',
        reverse('infinite_scrolling:page:list')
    )

    return portal_views.delete_form_view(
        request,
        obj=infinite_scrolling,
        return_url=return_url
    )


def detail_page_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    infinite_scrolling = get_object_or_404(InfiniteScrolling, pk=pk)

    context_data = {
        'infinite_scrolling': infinite_scrolling,
    }

    return portal_views.detail_view(
        request,
        obj=infinite_scrolling,
        context_data=context_data,
        template='infinite_scrolling/page/detail_page.html'
    )


def list_page_view(request: WSGIRequest) -> TemplateResponse:
    infinite_scrolling = get_object_or_null_obj(InfiniteScrolling, pk=0)

    InfiniteScrolling.objects.process_session_filter(
        request=request,
        session_key=INFINITE_SCROLLING_FILTERING_SESSION_KEY,
        form_class=InfiniteScrollingListFilterForm,
    )

    dg.glue_model_object(request, 'infinite_scrolling', infinite_scrolling)

    context_data = {
        'endpoint': reverse('infinite_scrolling:template:items'),
        'filter_session': SessionController(request, INFINITE_SCROLLING_FILTERING_SESSION_KEY),
    }

    return TemplateResponse(
        request=request,
        context=context_data,
        template='infinite_scrolling/page/list_page.html',
    )


def table_page_view(request: WSGIRequest) -> TemplateResponse:
    infinite_scrolling = get_object_or_null_obj(InfiniteScrolling, pk=0)

    InfiniteScrolling.objects.process_session_filter(
        request=request,
        session_key=INFINITE_SCROLLING_FILTERING_SESSION_KEY,
        form_class=InfiniteScrollingListFilterForm,
    )

    dg.glue_model_object(request, 'infinite_scrolling', infinite_scrolling)

    context_data = {
        'endpoint': reverse('infinite_scrolling:template:rows'),
        'filter_session': SessionController(request, INFINITE_SCROLLING_FILTERING_SESSION_KEY),
    }

    return TemplateResponse(
        request=request,
        context=context_data,
        template='infinite_scrolling/page/table_page.html',
    )
