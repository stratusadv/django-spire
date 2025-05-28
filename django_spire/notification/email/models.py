from django.db import models

from django_spire.notification.models import Notification
from django_spire.notification.email.querysets import EmailNotificationQuerySet


class EmailNotification(models.Model):
    notification = models.OneToOneField(
        Notification,
        editable=False,
        on_delete=models.CASCADE,
        related_name='email',
        related_query_name='email',
    )
    to_email_address = models.EmailField()
    template_id = models.CharField(max_length=64, default='')
    context_data = models.JSONField(default=dict)
    cc = models.JSONField(default=list)
    bcc = models.JSONField(default=list)

    objects = EmailNotificationQuerySet.as_manager()

    def __str__(self):
        return f'{self.notification.title} - {self.to_email_address}'

    class Meta:
        db_table = 'django_spire_notification_email'
        verbose_name = 'Email Notification'
        verbose_name_plural = 'Email Notifications'
