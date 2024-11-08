from __future__ import annotations

from typing_extensions import TYPE_CHECKING

from django.shortcuts import get_object_or_404

from django_spire.views import portal_views

from example.gamification import models

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest
    from django.template.response import TemplateResponse


def gamification_detail_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    gamification = get_object_or_404(models.GamificationExample, pk=pk)

    context_data = {
        'gamification': gamification,
    }

    return portal_views.detail_view(
        request,
        obj=gamification,
        context_data=context_data,
        template='gamification/page/gamification_detail_page.html'
    )


def gamification_list_view(request: WSGIRequest) -> TemplateResponse:
    context_data = {
        'gamifications': models.GamificationExample.objects.all()
    }

    return portal_views.list_view(
        request,
        model=models.GamificationExample,
        context_data=context_data,
        template='gamification/page/gamification_list_page.html'
    )
