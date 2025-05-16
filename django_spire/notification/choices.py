from __future__ import annotations

from django.db import models


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
