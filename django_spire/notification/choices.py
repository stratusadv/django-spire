from __future__ import annotations

from enum import Enum

from django.db import models

from django_spire.notification.email.sender import EmailNotificationSender


class NotificationTypeChoices(models.TextChoices):
    APP = 'app'
    EMAIL = 'email'
    PUSH = 'push'
    SMS = 'sms'

    def send(self) -> None:
        sender_class = NotificationSenderMap(self.value).value
        sender = sender_class(self)
        sender.send()


class NotificationPriorityChoices(models.TextChoices):
    LOW = 'low'
    MEDIUM = 'medium'
    HIGH = 'high'


class NotificationSenderMap(Enum):
    EMAIL = EmailNotificationSender
    # SMS = EmailNotificationSender
    # PUSH = EmailNotificationSender
