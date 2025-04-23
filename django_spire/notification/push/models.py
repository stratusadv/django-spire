from django.db import models

from django_spire.history.mixins import HistoryModelMixin


class PushNotification(HistoryModelMixin):

    class Meta:
        db_table = 'django_spire_notification_push'
        verbose_name = 'Push Notification'
        verbose_name_plural = 'Push Notifications'