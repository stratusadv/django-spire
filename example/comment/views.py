from __future__ import annotations

from typing_extensions import TYPE_CHECKING

from django.shortcuts import get_object_or_404

from django_spire.views import portal_views

from example.comment import models

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest
    from django.template.response import TemplateResponse


def comment_detail_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    comment = get_object_or_404(models.CommentExample, pk=pk)

    context_data = {
        'comment': comment,
    }

    return portal_views.detail_view(
        request,
        obj=comment,
        context_data=context_data,
        template='comment/page/comment_detail_page.html'
    )


def comment_list_view(request: WSGIRequest) -> TemplateResponse:
    context_data = {
        'comments': models.CommentExample.objects.all()
    }

    return portal_views.list_view(
        request,
        model=models.CommentExample,
        context_data=context_data,
        template='comment/page/comment_list_page.html'
    )
