from __future__ import annotations

from typing_extensions import TYPE_CHECKING

from django.shortcuts import get_object_or_404

from django_spire.views import portal_views

from examples.breadcrumb import models

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest
    from django.template.response import TemplateResponse


def breadcrumb_detail_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    breadcrumb = get_object_or_404(models.BreadcrumbExample, pk=pk)

    context_data = {
        'breadcrumb': breadcrumb,
    }

    return portal_views.detail_view(
        request,
        obj=breadcrumb,
        context_data=context_data,
        template='breadcrumb/page/breadcrumb_detail_page.html'
    )
