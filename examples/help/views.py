from __future__ import annotations

from typing_extensions import TYPE_CHECKING

from django.shortcuts import get_object_or_404

from django_spire.views import portal_views

from examples.help import models

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest
    from django.template.response import TemplateResponse


def help_detail_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    help_model = get_object_or_404(models.HelpExample, pk=pk)

    context_data = {
        'help': help_model,
    }

    return portal_views.detail_view(
        request,
        obj=help_model,
        context_data=context_data,
        template='help/page/help_detail_page.html'
    )
