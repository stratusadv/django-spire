from __future__ import annotations

from django.contrib.auth.models import User
from django.db import models
from django.utils.timezone import now
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

from django_spire.history.mixins import HistoryModelMixin
from django_spire.notification.choices import (
    NotificationTypeChoices, NotificationPriorityChoices, NotificationStatusChoices
)
from django_spire.notification.querysets import NotificationQuerySet


class Notification(HistoryModelMixin):
    user = models.ForeignKey(
        User,
        editable=False,
        on_delete=models.DO_NOTHING,
        blank=True,
        null=True,
        related_name='notifications',
        related_query_name='notification'
    )

    type = models.CharField(max_length=32, default=NotificationTypeChoices.EMAIL, choices=NotificationTypeChoices.choices)
    title = models.CharField(max_length=124)
    body = models.TextField(default='')
    url = models.CharField(max_length=255, default='')
    status = models.CharField(max_length=32, default=NotificationStatusChoices.PENDING, choices=NotificationStatusChoices.choices)
    priority = models.CharField(
        max_length=32,
        default=NotificationPriorityChoices.LOW,
        choices=NotificationPriorityChoices.choices
    )

    publish_datetime = models.DateTimeField(default=now)
    sent_datetime = models.DateTimeField(blank=True, null=True)

    content_object = GenericForeignKey('content_type', 'object_id')
    content_type = models.ForeignKey(
        ContentType,
        related_name='django_spire_notification',
        on_delete=models.CASCADE,
        editable=False,
        null=True,
        blank=True
    )
    object_id = models.PositiveIntegerField(null=True, blank=True)

    objects = NotificationQuerySet.as_manager()

    class Meta:
        db_table = 'django_spire_notification'
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
