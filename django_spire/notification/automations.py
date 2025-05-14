from __future__ import annotations

from django_spire.notification.managers import NotificationManager


def process_notifications() -> str:
    NotificationManager().process_ready_to_send()

    return 'Successfully Completed'
