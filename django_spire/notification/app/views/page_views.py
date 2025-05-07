from __future__ import annotations

from typing_extensions import TYPE_CHECKING

from django_spire.contrib.generic_views import portal_views

from django_spire.notification.app.models import AppNotification

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest
    from django.template.response import TemplateResponse


def app_notification_list_view(request: WSGIRequest) -> TemplateResponse:
    app_notification_list = (
        AppNotification.objects.by_user(request.user)
        .active()
        .annotate_is_viewed_by_user(request.user)
        .order_by("-created_datetime")
    )

    return portal_views.list_view(
        request,
        context_data={'notification_list': app_notification_list},
        model=AppNotification,
        template='django_spire/notification/app/page/list_page.html'
    )
