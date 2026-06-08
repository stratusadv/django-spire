from __future__ import annotations

from typing import TYPE_CHECKING

from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.urls import reverse

from test_project.app.history import models

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


def history_detail_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    history = get_object_or_404(models.HistoryExample, pk=pk)

    context_data = {'history': history}
    context_data['page_title'] = str(history)
    context_data['page_description'] = 'Detail View'
    context_data['breadcrumbs'] = [
        {'name': 'History Examples', 'href': reverse('history:page:list')},
        {'name': str(history), 'href': None},
    ]
    return TemplateResponse(
        request, context=context_data, template='history/page/history_detail_page.html'
    )


def history_home_view(request: WSGIRequest) -> TemplateResponse:
    template = 'history/page/history_home_page.html'
    return TemplateResponse(request, template)


def history_list_view(request: WSGIRequest) -> TemplateResponse:
    context_data = {'history': models.HistoryExample.objects.all()}
    context_data['page_title'] = 'History Example'
    context_data['page_description'] = 'List View'
    context_data['breadcrumbs'] = [{'name': 'History Examples', 'href': None}]

    return TemplateResponse(
        request, context=context_data, template='history/page/history_list_page.html'
    )
