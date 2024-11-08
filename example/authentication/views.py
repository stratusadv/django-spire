from __future__ import annotations

from typing_extensions import TYPE_CHECKING

from django.shortcuts import get_object_or_404

from django_spire.views import portal_views

from example.authentication import models


if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest
    from django.template.response import TemplateResponse


def authentication_detail_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    authentication = get_object_or_404(models.AuthenticationExample, pk=pk)

    context_data = {
        'authentication': authentication,
    }

    return portal_views.detail_view(
        request,
        obj=authentication,
        context_data=context_data,
        template='authentication/page/authentication_detail_page.html'
    )


def authentication_list_view(request: WSGIRequest) -> TemplateResponse:
    context_data = {
        'authentication': models.AuthenticationExample.objects.all()
    }

    return portal_views.list_view(
        request,
        model=models.AuthenticationExample,
        context_data=context_data,
        template='authentication/page/authentication_list_page.html'
    )
