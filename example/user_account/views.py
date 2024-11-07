from __future__ import annotations

from typing_extensions import TYPE_CHECKING

from django.shortcuts import get_object_or_404

from django_spire.views import portal_views

from example.user_account import models

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest
    from django.template.response import TemplateResponse


def user_account_detail_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    user_account = get_object_or_404(models.UserAccount, pk=pk)

    context_data = {
        'user_account': user_account,
    }

    return portal_views.detail_view(
        request,
        obj=user_account,
        context_data=context_data,
        template='user_account/page/user_account_detail_page.html'
    )
