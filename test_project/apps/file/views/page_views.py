from __future__ import annotations

from typing import TYPE_CHECKING

from django.shortcuts import get_object_or_404

from django_spire.contrib.generic_views import portal_views

from test_project.apps.file import models

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest
    from django.template.response import TemplateResponse


def detail_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    file_example = get_object_or_404(models.FileExample, pk=pk)

    context_data = {
        'file_example': file_example,
    }

    return portal_views.detail_view(
        request,
        obj=file_example,
        context_data=context_data,
        template='file/page/detail_page.html'
    )


def list_view(request: WSGIRequest) -> TemplateResponse:
    context_data = {
        'file_examples': models.FileExample.objects.active()
    }

    return portal_views.list_view(
        request,
        model=models.FileExample,
        context_data=context_data,
        template='file/page/list_page.html'
    )
