from __future__ import annotations

from typing_extensions import TYPE_CHECKING

from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse

from django_spire.views import portal_views

from example.home import models

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


def home_detail_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    home = get_object_or_404(models.HomeExample, pk=pk)

    context_data = {
        'home': home,
    }

    return portal_views.detail_view(
        request,
        obj=home,
        context_data=context_data,
        template='home/page/home_detail_page.html'
    )


def home_home_view(request: WSGIRequest) -> TemplateResponse:
    template = 'home/page/home_home_page.html'
    return TemplateResponse(request, template)


def home_list_view(request: WSGIRequest) -> TemplateResponse:
    context_data = {
        'home': models.HomeExample.objects.all()
    }

    return portal_views.list_view(
        request,
        model=models.HomeExample,
        context_data=context_data,
        template='home/page/home_list_page.html'
    )
