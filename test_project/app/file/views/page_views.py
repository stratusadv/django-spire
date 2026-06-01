from __future__ import annotations

from typing import TYPE_CHECKING

from django.shortcuts import get_object_or_404

from django_spire.contrib.generic_views import page_views

from test_project.app.file import models

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest
    from django.template.response import TemplateResponse


def detail_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    file_example = get_object_or_404(models.FileExample, pk=pk)

    context_data = {
        'file_example': file_example,
    }

    return generic_views.detail_view(
        request,
        obj=file_example,
        context_data=context_data,
        template='file/page/detail_page.html'
    )


def list_view(request: WSGIRequest) -> TemplateResponse:
    context_data = {
        'file_examples': models.FileExample.objects.active()
    }

    return generic_views.list_view(
        request,
        model=models.FileExample,
        context_data=context_data,
        template='file/page/list_page.html'
    )
