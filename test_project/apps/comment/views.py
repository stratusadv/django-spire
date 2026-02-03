from __future__ import annotations

from typing import TYPE_CHECKING

from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse

from django_spire.contrib.generic_views import portal_views

from test_project.apps.comment import models

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


def comment_detail_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    comment = get_object_or_404(models.CommentExample, pk=pk)

    context_data = {
        'comment_example': comment,
    }

    return portal_views.detail_view(
        request,
        obj=comment,
        context_data=context_data,
        template='comment/page/comment_detail_page.html'
    )


def comment_home_view(request: WSGIRequest) -> TemplateResponse:
    template = 'comment/page/comment_list_page.html'
    return TemplateResponse(request, template)


def comment_list_view(request: WSGIRequest) -> TemplateResponse:
    context_data = {
        'comment_examples': models.CommentExample.objects.all()
    }

    return portal_views.list_view(
        request,
        model=models.CommentExample,
        context_data=context_data,
        template='comment/page/comment_list_page.html'
    )


def comment_form_view(request: WSGIRequest) -> TemplateResponse:
    template = 'comment/page/comment_form.html'
    return TemplateResponse(request, template)