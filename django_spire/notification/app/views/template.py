from __future__ import annotations
import json
from typing_extensions import TYPE_CHECKING

from django.template.response import TemplateResponse

from django_spire.notification.app.models import AppNotification

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest

def notification_dropdown_template_view(request: WSGIRequest) -> TemplateResponse:
    notification_list = AppNotification.objects.active().by_user(request.user).order_by('-created_datetime').select_related('notification')

    return TemplateResponse(
        request,
        context={
            'notification_list': json.dumps([notification.as_dict() for notification in notification_list]),
        },
        template='spire/notification/app/dropdown/notification_dropdown_content.html'
    )
