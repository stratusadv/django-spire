from django.db import models

from django_spire.notification.models import Notification
from django_spire.notification.sms.querysets import SmsNotificationQuerySet


class SmsNotification(models.Model):
    notification = models.OneToOneField(
        Notification,
        editable=False,
        on_delete=models.CASCADE,
        related_name='sms',
        related_query_name='sms',
    )
    to_phone_number = models.CharField(max_length=11, blank=True)

    objects = SmsNotificationQuerySet.as_manager()

    def __str__(self):
        return f'{self.to_phone_number} - {self.notification.title}'

    class Meta:
        db_table = 'django_spire_notification_sms'
        verbose_name = 'SMS Notification'
        verbose_name_plural = 'SMS Notifications'
