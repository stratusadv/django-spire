from __future__ import annotations

from typing_extensions import TYPE_CHECKING

from django.shortcuts import get_object_or_404

from django_spire.views import portal_views

from example.notification import models

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest
    from django.template.response import TemplateResponse


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
