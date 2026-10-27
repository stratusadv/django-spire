from __future__ import annotations

from typing import TYPE_CHECKING

from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse

from django_spire.comment.navigation import CommentNavigation
from test_project.app.comment import models

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


def comment_detail_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    comment = get_object_or_404(models.CommentExample, pk=pk)

    nav = CommentNavigation()
    nav.breadcrumbs.add(str(comment), None)
    nav.page_title = str(comment)
    context = nav.as_context()
    context['comment_example'] = comment
    context['page_description'] = 'Detail View'

    return TemplateResponse(
        request, context=context, template='comment/page/comment_detail_page.html'
    )
