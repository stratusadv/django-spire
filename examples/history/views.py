from __future__ import annotations

from typing_extensions import TYPE_CHECKING

from django.shortcuts import get_object_or_404

from django_spire.views import portal_views

from examples.history import models

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest
    from django.template.response import TemplateResponse


def history_detail_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    history = get_object_or_404(models.HistoryExample, pk=pk)

    context_data = {
        'history': history,
    }

    return portal_views.detail_view(
        request,
        obj=history,
        context_data=context_data,
        template='history/page/history_detail_page.html'
    )
