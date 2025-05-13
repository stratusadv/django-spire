from __future__ import annotations

from django_spire.notification.processors import NotificationProcessor


def process_notifications() -> str:
    NotificationProcessor().process_all()

    return 'Successfully Completed'
