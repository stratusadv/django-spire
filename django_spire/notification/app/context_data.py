from __future__ import annotations
import json
from typing_extensions import TYPE_CHECKING

from django_spire.notification.app.models import AppNotification

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


def app_notification_dropdown_context_data(user: WSGIRequest) -> dict:
    app_notification_list = (
        AppNotification.objects.active()
        .annotate_is_viewed_by_user(user)
        .order_by('-created_datetime')
        .select_related('notification')
        .distinct()
    )

    formatted_notification_data = [
        {
            'id': app_notification.id,
            'title': app_notification.notification.title,
            'body': app_notification.notification.message,
            'url': app_notification.notification.url,
            'time_since_delivered': app_notification.verbose_time_since_delivered,
            'viewed': app_notification.viewed
        }
        for app_notification in app_notification_list
    ]

    return {
        'notification_list_json': json.dumps(formatted_notification_data),
    }
