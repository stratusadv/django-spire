from __future__ import annotations

from typing_extensions import TYPE_CHECKING

from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse

from django_spire.contrib.generic_views import portal_views

from example.user_account.profile import models

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


def profile_detail_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    profile = get_object_or_404(models.UserAccountProfileExample, pk=pk)

    context_data = {
        'profile': profile,
    }

    return portal_views.detail_view(
        request,
        obj=profile,
        context_data=context_data,
        template='user_account/profile/page/user_account_profile_detail_page.html'
    )


def profile_home_view(request: WSGIRequest) -> TemplateResponse:
    template = 'user_account/profile/page/user_account_profile_home_page.html'
    return TemplateResponse(request, template)


def profile_list_view(request: WSGIRequest) -> TemplateResponse:
    context_data = {
        'profiles': models.UserAccountProfileExample.objects.all()
    }

    return portal_views.list_view(
        request,
        model=models.UserAccountProfileExample,
        context_data=context_data,
        template='user_account/profile/page/user_account_profile_list_page.html'
    )
