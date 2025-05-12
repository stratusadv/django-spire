from __future__ import annotations

from django.db import models

from django_spire.notification.maps import NotificationProcessorMap


class NotificationPriorityChoices(models.TextChoices):
    LOW = 'low'
    MEDIUM = 'medium'
    HIGH = 'high'


class NotificationStatusChoices(models.TextChoices):
    PENDING = 'pending'
    PROCESSING = 'processing'
    SENT = 'sent'
    ERRORED = 'errored'
    FAILED = 'failed'


class NotificationTypeChoices(models.TextChoices):
    APP = 'app'
    EMAIL = 'email'
    PUSH = 'push'
    SMS = 'sms'

    def send(self) -> None:
        sender_class = NotificationProcessorMap(self.value).value
        sender = sender_class(self)
        sender.send()
