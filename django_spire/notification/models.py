from __future__ import annotations

from django.db import models
from django.utils.timezone import now

from django_spire.history.mixins import HistoryModelMixin
from django_spire.notification.choices import (
    NotificationSenderMap,
    NotificationTypeChoices
)

class Notification(HistoryModelMixin):
    type = models.CharField(max_length=32, default=NotificationTypeChoices.EMAIL, choices=NotificationTypeChoices.choices)
    title = models.CharField(max_length=124)
    body = models.TextField(default='')
    processed_datetime = models.DateTimeField(blank=True, null=True)
    url = models.CharField(max_length=255, default='')
    is_processed = models.BooleanField(default=False)

    def mark_processed(self) -> None:
        self.processed = True
        self.processed_datetime = now()
        self.save()

    def send(self) -> None:
        sender_class = NotificationSenderMap(self.type).value
        sender = sender_class(self)
        sender.send()

    class Meta:
        db_table = 'spire_notification'
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
