from __future__ import annotations

from typing_extensions import TYPE_CHECKING

from django.shortcuts import get_object_or_404

from django_spire.views import portal_views

from examples.placeholder import models

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest
    from django.template.response import TemplateResponse


def placeholder_detail_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    placeholder = get_object_or_404(models.Placeholder, pk=pk)

    context_data = {
        'placeholder': placeholder,
    }

    return portal_views.detail_view(
        request,
        obj=placeholder,
        context_data=context_data,
        template='placeholder/page/placeholder_detail_page.html'
    )
