from __future__ import annotations

from django_spire.core.decorators import close_db_connections
from django_spire.notification.managers import NotificationManager


@close_db_connections
def process_notifications() -> str:
    NotificationManager().process_ready_notifications()

    return 'Successfully Completed'
