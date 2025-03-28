from __future__ import annotations

from typing_extensions import TYPE_CHECKING

from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse

from django_spire.views import portal_views

from example.options import models

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


def options_detail_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    options = get_object_or_404(models.OptionsExample, pk=pk)

    context_data = {
        'options': options,
    }

    return portal_views.detail_view(
        request,
        obj=options,
        context_data=context_data,
        template='options/page/options_detail_page.html'
    )


def options_home_view(request: WSGIRequest) -> TemplateResponse:
    template = 'options/page/options_home_page.html'
    return TemplateResponse(request, template)


def options_list_view(request: WSGIRequest) -> TemplateResponse:
    context_data = {
        'options': models.OptionsExample.objects.all()
    }

    return portal_views.list_view(
        request,
        model=models.OptionsExample,
        context_data=context_data,
        template='options/page/options_list_page.html'
    )
