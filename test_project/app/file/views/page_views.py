from __future__ import annotations

from typing import TYPE_CHECKING

from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.urls import reverse

from django_spire.file.navigation import FileNavigation
from test_project.app.file import models

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


def detail_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    file_example = get_object_or_404(models.FileExample, pk=pk)

    nav = FileNavigation()
    nav.page_title = str(file_example)
    context = nav.as_context()
    context['file_example'] = file_example
    context['page_title'] = str(file_example)
    context['page_description'] = 'Detail View'

    return TemplateResponse(request, context=context, template='file/page/detail_page.html')


def list_view(request: WSGIRequest) -> TemplateResponse:
    nav = FileNavigation()
    context = nav.as_context()
    context['file_examples'] = models.FileExample.objects.active()
    context['page_title'] = 'File Example'
    context['page_description'] = 'List View'

    return TemplateResponse(request, context=context, template='file/page/list_page.html')
