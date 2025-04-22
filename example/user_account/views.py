from __future__ import annotations

from typing_extensions import TYPE_CHECKING

from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse

from django_spire.contrib.generic_views import portal_views

from example.user_account import models

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


def user_account_detail_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    user_account = get_object_or_404(models.UserAccountExample, pk=pk)

    context_data = {
        'user_account': user_account,
    }

    return portal_views.detail_view(
        request,
        obj=user_account,
        context_data=context_data,
        template='user_account/page/user_account_detail_page.html'
    )


def user_account_home_view(request: WSGIRequest) -> TemplateResponse:
    template = 'user_account/page/user_account_home_page.html'
    return TemplateResponse(request, template)


def user_account_list_view(request: WSGIRequest) -> TemplateResponse:
    context_data = {
        'user_accounts': models.UserAccountExample.objects.all()
    }

    return portal_views.list_view(
        request,
        model=models.UserAccountExample,
        context_data=context_data,
        template='user_account/page/user_account_list_page.html'
    )
