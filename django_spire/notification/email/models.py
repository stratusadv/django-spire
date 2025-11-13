from django.db import models

from django_spire.file.models import File
from django_spire.notification.email.querysets import EmailNotificationQuerySet
from django_spire.notification.models import Notification


class EmailNotification(models.Model):
    """
    It is important to note size limits for email content contained in this model. E.g., Sendgrid has a hard total email
    limit of 30mb (and a recommended limit of 10mb for attachments): https://www.twilio.com/docs/sendgrid/ui/sending-email/attachments-with-digioh#-Limitations
    """
    notification = models.OneToOneField(
        Notification,
        editable=False,
        on_delete=models.CASCADE,
        related_name='email',
        related_query_name='email',
    )

    attachments = models.ManyToManyField(
        File,
        blank=True,
        related_name='attachments',
        related_query_name='attachment',
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
