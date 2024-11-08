from __future__ import annotations

from typing_extensions import TYPE_CHECKING

from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse

from django_spire.views import portal_views

from example.file import models

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


def file_detail_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    file = get_object_or_404(models.FileExample, pk=pk)

    context_data = {
        'file': file,
    }

    return portal_views.detail_view(
        request,
        obj=file,
        context_data=context_data,
        template='file/page/file_detail_page.html'
    )


def file_home_view(request: WSGIRequest) -> TemplateResponse:
    template = 'file/page/file_home_page.html'
    return TemplateResponse(request, template)


def file_list_view(request: WSGIRequest) -> TemplateResponse:
    context_data = {
        'files': models.FileExample.objects.all()
    }

    return portal_views.list_view(
        request,
        model=models.FileExample,
        context_data=context_data,
        template='file/page/file_list_page.html'
    )
