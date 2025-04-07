import json
from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.utils.timezone import localtime

from django_spire.history.mixins import HistoryModelMixin
from django_spire.history.viewed.mixins import ViewedModelMixin
from django_spire.notification.models import Notification
from django_spire.notification.app.querysets import AppNotificationQuerySet

class AppNotification(ViewedModelMixin, HistoryModelMixin):
    notification = models.OneToOneField(Notification, editable=False, on_delete=models.CASCADE)
    user = models.ForeignKey(User, editable=False, on_delete=models.CASCADE)
    url = models.CharField(max_length=255, default='')

    content_object = GenericForeignKey('content_type', 'object_id')
    content_type = models.ForeignKey(ContentType, related_name='spire_appnotification', on_delete=models.CASCADE, editable=False)
    object_id = models.PositiveIntegerField()

    objects = AppNotificationQuerySet.as_manager()

    def __str__(self):
        return f'{self.notification.title}'

    @property
    def verbose_time_since_creation(self) -> str:
        delta = localtime() - self.created_datetime

        seconds = abs(delta.total_seconds())
        minutes = seconds // 60
        hours = minutes // 60
        days = hours // 24

        if days > 0:
            return f"{int(days)} day{'s' if days != 1 else ''} ago"
        elif hours > 0:
            return f"{int(hours)} hour{'s' if hours != 1 else ''} ago"
        elif minutes > 0:
            return f"{int(minutes)} minute{'s' if minutes != 1 else ''} ago"
        else:
            return "just now"

    def as_dict(self) -> dict:
        return {
            'id': self.id,
            'title': self.notification.title,
            'body': self.notification.body,
            'url': self.notification.url,
            'time_since_creation': self.verbose_time_since_creation,
            # 'viewed': self.is_viewed(self.user)
        }

    def as_json(self) -> str:
        return json.dumps(self.as_dict())

    class Meta:
        db_table = 'spire_notification_app'
        verbose_name = 'App Notification'
        verbose_name_plural = 'App Notifications'

