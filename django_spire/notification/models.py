from __future__ import annotations

from django.db import models
from django.contrib.contenttypes.models import ContentType

from django.utils.timezone import now

from django_spire.history.mixins import HistoryModelMixin
from django_spire.notification.enums import (
    NotificationSenderMap,
    NotificationTypeChoices
)

class Notification(HistoryModelMixin):
    type = models.CharField(max_length=32, default=NotificationTypeChoices.EMAIL)
    title = models.CharField(max_length=124)
    body = models.TextField(default='')
    sent_datetime = models.DateTimeField(default=now)
    url = models.CharField(max_length=255, default='')
    processed = models.BooleanField(default=False)

    def mark_sent(self) -> None:
        self.is_sent = True
        self.sent_datetime = now()
        self.save()

    def send(self) -> None:
        sender_class = NotificationSenderMap(self.type).value
        sender = sender_class(self)
        sender.send()

    class Meta:
        db_table = 'spire_notification'
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'


# class Notification(models.Model):
#     type = models.CharField(max_length=32, default=NotificationTypeChoices.EMAIL)

#     email = models.EmailField(default='')
#     name = models.CharField(max_length=124, null=True, blank=True)
#     title = models.CharField(max_length=128, default='')
#     body = models.TextField(default='')
#     url = models.CharField(max_length=255, default='')

#     send_datetime = models.DateTimeField(default=now)

#     created_datetime = models.DateTimeField(default=now)
#     sent_datetime = models.DateTimeField(null=True, blank=True)
#     is_sent = models.BooleanField(default=False)

#     def mark_sent(self) -> None:
#         self.is_sent = True
#         self.sent_datetime = now()
#         self.save()

#     def send(self) -> None:
#         sender_class = NotificationSenderEnum(self.type).value
#         sender = sender_class(self)
#         sender.send()

#     class Meta:
#         db_table = 'spire_notification'
#         verbose_name = 'Notification'
#         verbose_name_plural = 'Notifications'
