from __future__ import annotations

from django_spire.notification.models import Notification


def process_notifications() -> str:
    for notification in Notification.objects.not_processed():
        notification.send()

    return 'Successfully Completed'
