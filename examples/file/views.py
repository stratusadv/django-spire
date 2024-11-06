from __future__ import annotations

from typing_extensions import TYPE_CHECKING

from django.shortcuts import get_object_or_404

from django_spire.views import portal_views

from examples.file import models

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest
    from django.template.response import TemplateResponse


def file_detail_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    file = get_object_or_404(models.File, pk=pk)

    context_data = {
        'file': file,
    }

    return portal_views.detail_view(
        request,
        obj=file,
        context_data=context_data,
        template='file/page/file_detail_page.html'
    )
