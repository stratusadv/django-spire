from __future__ import annotations

from typing_extensions import TYPE_CHECKING

from django.shortcuts import get_object_or_404

from django_spire.views import portal_views

from example.user_account.profile import models

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest
    from django.template.response import TemplateResponse


def profile_detail_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    profile = get_object_or_404(models.UserAccountProfile, pk=pk)

    context_data = {
        'profile': profile,
    }

    return portal_views.detail_view(
        request,
        obj=profile,
        context_data=context_data,
        template='profile/page/profile_detail_page.html'
    )
