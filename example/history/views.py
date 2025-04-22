from __future__ import annotations

from typing_extensions import TYPE_CHECKING

from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse

from django_spire.contrib.generic_views import portal_views

from example.history import models

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


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


def history_home_view(request: WSGIRequest) -> TemplateResponse:
    template = 'history/page/history_home_page.html'
    return TemplateResponse(request, template)


def history_list_view(request: WSGIRequest) -> TemplateResponse:
    context_data = {
        'history': models.HistoryExample.objects.all()
    }

    return portal_views.list_view(
        request,
        model=models.HistoryExample,
        context_data=context_data,
        template='history/page/history_list_page.html'
    )
