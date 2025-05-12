from __future__ import annotations

from enum import Enum

from django_spire.notification.email.sender import EmailNotificationSender


class NotificationProcessorMap(Enum):
    EMAIL = EmailNotificationProcessor
    # SMS = EmailNotificationSender
    # PUSH = EmailNotificationSender
