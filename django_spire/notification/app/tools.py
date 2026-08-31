from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from django_spire.notification.app.models import AppNotification


def app_notification_verbose_time_since_delivered(app_notification: AppNotification) -> str:
    return app_notification.verbose_time_since_delivered
