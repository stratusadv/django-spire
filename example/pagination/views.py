from __future__ import annotations

from typing_extensions import TYPE_CHECKING

from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse

from django_spire.views import portal_views

from example.pagination import models

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


def pagination_detail_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    pagination = get_object_or_404(models.PaginationExample, pk=pk)

    context_data = {
        'pagination': pagination,
    }

    return portal_views.detail_view(
        request,
        obj=pagination,
        context_data=context_data,
        template='pagination/page/pagination_detail_page.html'
    )


def pagination_home_view(request: WSGIRequest) -> TemplateResponse:
    template = 'pagination/page/pagination_home_page.html'
    return TemplateResponse(request, template)


def pagination_list_view(request: WSGIRequest) -> TemplateResponse:
    context_data = {
        'paginations': models.PaginationExample.objects.all()
    }

    return portal_views.list_view(
        request,
        model=models.PaginationExample,
        context_data=context_data,
        template='pagination/page/pagination_list_page.html'
    )
