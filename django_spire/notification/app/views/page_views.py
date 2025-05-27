from __future__ import annotations

from django.contrib.auth.decorators import login_required
from typing_extensions import TYPE_CHECKING

from django_spire.contrib.generic_views import portal_views

from django_spire.notification.app.models import AppNotification

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest
    from django.template.response import TemplateResponse


@login_required()
def app_notification_list_view(request: WSGIRequest) -> TemplateResponse:
    app_notification_list = (
        AppNotification.objects.active()
        .is_sent()
        .annotate_is_viewed_by_user(request.user)
        .select_related('notification')
        .distinct()
        .order_by('-notification__sent_datetime')
    )

    return portal_views.list_view(
        request,
        context_data={'notification_list': app_notification_list},
        model=AppNotification,
        template='django_spire/notification/app/page/list_page.html'
    )
