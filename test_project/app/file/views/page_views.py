from __future__ import annotations

from typing import TYPE_CHECKING

from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.urls import reverse

from test_project.app.file import models

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


def detail_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    file_example = get_object_or_404(models.FileExample, pk=pk)

    context_data = {'file_example': file_example}
    context_data['page_title'] = str(file_example)
    context_data['page_description'] = 'Detail View'
    context_data['breadcrumbs'] = [
        {'name': 'File Examples', 'href': reverse('file:page:list')},
        {'name': str(file_example), 'href': None},
    ]
    return TemplateResponse(request, context=context_data, template='file/page/detail_page.html')


def list_view(request: WSGIRequest) -> TemplateResponse:
    context_data = {'file_examples': models.FileExample.objects.active()}
    context_data['page_title'] = 'File Example'
    context_data['page_description'] = 'List View'
    context_data['breadcrumbs'] = [{'name': 'File Examples', 'href': None}]

    return TemplateResponse(request, context=context_data, template='file/page/list_page.html')
