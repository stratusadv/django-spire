from __future__ import annotations

from typing_extensions import TYPE_CHECKING

from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse

from django_spire.contrib.generic_views import portal_views

from example.search import models

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


def search_detail_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    search = get_object_or_404(models.SearchExample, pk=pk)

    context_data = {
        'search': search,
    }

    return portal_views.detail_view(
        request,
        obj=search,
        context_data=context_data,
        template='search/page/search_detail_page.html'
    )


def search_home_view(request: WSGIRequest) -> TemplateResponse:
    template = 'search/page/search_home_page.html'
    return TemplateResponse(request, template)


def search_list_view(request: WSGIRequest) -> TemplateResponse:
    context_data = {
        'search': models.SearchExample.objects.all()
    }

    return portal_views.list_view(
        request,
        model=models.SearchExample,
        context_data=context_data,
        template='search/page/search_list_page.html'
    )
