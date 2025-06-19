from django.contrib.sites.models import Site
from django.db import models
from django.urls import reverse
from django.utils.timezone import now

from django_spire.notification.models import Notification
from django_spire.notification.sms.choices import SmsMediaContentTypeChoices
from django_spire.notification.sms.querysets import SmsNotificationQuerySet, \
    SmsTemporaryMediaQuerySet


class SmsTemporaryMedia(models.Model):
    content = models.TextField()
    content_type = models.CharField(max_length=64, choices=SmsMediaContentTypeChoices)
    name = models.CharField(max_length=255)
    expire_datetime = models.DateTimeField()
    external_access_key = models.UUIDField(unique=True)

    objects = SmsTemporaryMediaQuerySet.as_manager()

    def __str__(self):
        return f'{self.name} - {self.content_type}'

    @property
    def external_url(self) -> str:
        path = reverse(
            'django_spire:notification:sms:media:temporary_media',
            kwargs={'external_access_key': self.external_access_key},
        )[1:]

        return f'{Site.objects.get_current()}/{path}'

    def is_expired(self) -> bool:
        return self.expire_datetime < now()

    def is_ready_for_deletion(self) -> bool:
        return not self.has_unsent_notifications() or self.is_expired()

    def has_unsent_notifications(self) -> bool:
        return self.sms_notifications.notification.unsent().active().exists()

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
    media_url = models.URLField(max_length=255, blank=True, null=True)

    objects = SmsNotificationQuerySet.as_manager()

    def __str__(self):
        return f'{self.to_phone_number} - {self.notification.title}'

    class Meta:
        db_table = 'django_spire_notification_sms'
        verbose_name = 'SMS Notification'
        verbose_name_plural = 'SMS Notifications'
