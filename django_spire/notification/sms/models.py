from django.db import models
from django.utils.timezone import now

from django_spire.notification.models import Notification
from django_spire.notification.sms.choices import SmsMediaTypeChoices
from django_spire.notification.sms.querysets import SmsNotificationQuerySet, \
    SmsTemporaryMediaQuerySet


class SmsTemporaryMedia(models.Model):
    content = models.TextField()
    content_type = models.CharField(max_length=64, choices=SmsMediaTypeChoices)
    name = models.CharField(max_length=255)
    expire_datetime = models.DateTimeField()
    external_access_key = models.UUIDField(unique=True)
    external_url = models.URLField(max_length=255, blank=True, null=True)

    objects = SmsTemporaryMediaQuerySet.as_manager()

    def __str__(self):
        return f'{self.name} - {self.content_type}'

    def is_expired(self) -> bool:
        return self.expire_datetime < now()

    def has_unsent_notifications(self) -> bool:
        return self.sms_notifications.notification.unsent().active().exists()

    def is_ready_for_deletion(self) -> bool:
        return not self.has_unsent_notifications() or self.is_expired()

    class Meta:
        db_table = 'django_spire_notification_sms_temporary_media'
        verbose_name = 'SMS Temporary Media'
        verbose_name_plural = 'SMS Temporary Media'


class SmsNotification(models.Model):
    notification = models.OneToOneField(
        Notification,
        editable=False,
        on_delete=models.CASCADE,
        related_name='sms',
        related_query_name='sms',
    )
    temporary_media = models.ForeignKey(
        SmsTemporaryMedia,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='sms_notifications',
        related_query_name='sms_notification',
    )
    to_phone_number = models.CharField(max_length=11, blank=True)
    media_url = models.URLField(max_length=255, blank=True)

    objects = SmsNotificationQuerySet.as_manager()

    def has_media(self) -> bool:
        return bool(self.temporary_media)

    def __str__(self):
        return f'{self.to_phone_number} - {self.notification.title}'

    class Meta:
        db_table = 'django_spire_notification_sms'
        verbose_name = 'SMS Notification'
        verbose_name_plural = 'SMS Notifications'
