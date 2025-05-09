from __future__ import annotations

from django.db import models
from django.utils.timezone import now
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

from django_spire.history.mixins import HistoryModelMixin
from django_spire.notification.choices import (
    NotificationSenderMap,
    NotificationTypeChoices, NotificationPriorityChoices
)
from django_spire.notification.querysets import NotificationQuerySet


class Notification(HistoryModelMixin):
    type = models.CharField(max_length=32, default=NotificationTypeChoices.EMAIL, choices=NotificationTypeChoices.choices)
    title = models.CharField(max_length=124)
    body = models.TextField(default='')
    processed_datetime = models.DateTimeField(blank=True, null=True)
    url = models.CharField(max_length=255, default='')
    is_processed = models.BooleanField(default=False)
    priority = models.CharField(
        max_length=32,
        default=NotificationPriorityChoices.LOW,
        choices=NotificationPriorityChoices.choices
    )

    content_object = GenericForeignKey('content_type', 'object_id')
    content_type = models.ForeignKey(ContentType, related_name='django_spire_notification', on_delete=models.CASCADE, editable=False)
    object_id = models.PositiveIntegerField()

    objects = NotificationQuerySet.as_manager()

    def mark_processed(self) -> None:
        self.is_processed = True
        self.processed_datetime = now()
        self.save()

    def send(self) -> None:
        sender_class = NotificationSenderMap(self.type).value
        sender = sender_class(self)
        sender.send()

    class Meta:
        db_table = 'django_spire_notification'
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
