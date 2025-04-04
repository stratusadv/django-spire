from __future__ import annotations
from typing_extensions import TYPE_CHECKING

from django.template.response import TemplateResponse

from django_spire.notification.app.models import AppNotification

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest

def notification_dropdown_template_view(request: WSGIRequest) -> TemplateResponse:
    app_notification_list = (
        AppNotification.objects.active()
        .annotate_is_viewed_by_user(request.user)
        .order_by('-created_datetime')
        .select_related('notification')
        .distinct()
    )

    return TemplateResponse(
        request,
        context={
            'app_notification_list': app_notification_list,
        },
        template='spire/notification/app/dropdown/notification_dropdown_content.html'
    )
