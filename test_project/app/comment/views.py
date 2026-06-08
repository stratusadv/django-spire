from __future__ import annotations

from typing import TYPE_CHECKING

from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse

from test_project.app.comment import models

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


def comment_detail_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    comment = get_object_or_404(models.CommentExample, pk=pk)

    context_data = {'comment_example': comment}

    context_data['page_title'] = str(comment)
    context_data['page_description'] = 'Detail View'
    context_data['breadcrumbs'] = [
        {'name': 'Comment Examples', 'href': None},
        {'name': str(comment), 'href': None},
    ]

    return TemplateResponse(
        request, context=context_data, template='comment/page/comment_detail_page.html'
    )


def comment_home_view(request: WSGIRequest) -> TemplateResponse:
    template = 'comment/page/comment_list_page.html'
    return TemplateResponse(request, template)


def comment_list_view(request: WSGIRequest) -> TemplateResponse:
    context_data = {'comment_examples': models.CommentExample.objects.all()}
    context_data['page_title'] = 'Comment Example'
    context_data['page_description'] = 'List View'
    context_data['breadcrumbs'] = [{'name': 'Comment Examples', 'href': None}]

    return TemplateResponse(
        request, context=context_data, template='comment/page/comment_list_page.html'
    )


def comment_form_view(request: WSGIRequest) -> TemplateResponse:
    template = 'comment/page/comment_form.html'
    return TemplateResponse(request, template)
