from __future__ import annotations

from typing_extensions import TYPE_CHECKING

from django.shortcuts import get_object_or_404

from django_spire.views import portal_views

from example.authentication.mfa import models

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest
    from django.template.response import TemplateResponse


def authentication_mfa_detail_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    authentication_mfa = get_object_or_404(models.AuthenticationMfaExample, pk=pk)

    context_data = {
        'authentication_mfa': authentication_mfa,
    }

    return portal_views.detail_view(
        request,
        obj=authentication_mfa,
        context_data=context_data,
        template='authentication/mfa/page/authentication_mfa_detail_page.html'
    )
