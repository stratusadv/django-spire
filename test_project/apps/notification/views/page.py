from __future__ import annotations

from typing_extensions import TYPE_CHECKING

from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse

from django_spire.contrib.generic_views import portal_views

from test_project.apps.notification import models

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


def notification_detail_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    notification = get_object_or_404(models.NotificationExample, pk=pk)

    context_data = {
        'notification': notification,
    }

    return portal_views.detail_view(
        request,
        obj=notification,
        context_data=context_data,
        template='notification/page/notification_detail_page.html'
    )


def notification_home_view(request: WSGIRequest) -> TemplateResponse:
    template = 'notification/page/notification_home_page.html'
    return TemplateResponse(request, template)


def notification_list_view(request: WSGIRequest) -> TemplateResponse:
    context_data = {
        'notifications': models.NotificationExample.objects.all()
    }

    return portal_views.list_view(
        request,
        model=models.NotificationExample,
        context_data=context_data,
        template='notification/page/notification_list_page.html'
    )
