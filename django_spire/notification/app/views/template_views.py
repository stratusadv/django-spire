from __future__ import annotations

import json

from typing_extensions import TYPE_CHECKING

from django.template.response import TemplateResponse

from django_spire.notification.app.models import AppNotification

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


def notification_dropdown_template_view(request: WSGIRequest) -> TemplateResponse:
    app_notification_list = (
        AppNotification.objects.active()
        .is_sent()
        .annotate_is_viewed_by_user(request.user)
        .select_related('notification')
        .distinct()
        .ordered_by_priority_and_sent_datetime()
    )

    body_data = json.loads(request.body.decode('utf-8'))

    return TemplateResponse(
        request,
        context={
            'app_notification_list': app_notification_list,
            'app_notification_list_url': body_data.get('app_notification_list_url'),
        },
        template='django_spire/notification/app/dropdown/notification_dropdown_content.html'
    )
