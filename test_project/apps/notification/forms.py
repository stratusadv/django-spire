from __future__ import annotations

from django.utils.timezone import localtime
from typing_extensions import ClassVar

from django import forms

from django_spire.notification import models
from django_spire.notification.app.models import AppNotification
from django_spire.notification.choices import NotificationStatusChoices, \
    NotificationTypeChoices
from django_spire.notification.email.models import EmailNotification
from django_spire.notification.sms.models import SmsNotification


class NotificationForm(forms.ModelForm):
    def save(self, commit: bool = True):
        if self.instance.type == NotificationTypeChoices.APP:
            try:
                _ = self.instance.app
            except AppNotification.DoesNotExist:
                AppNotification.objects.create(notification=self.instance)

        elif self.instance.type == NotificationTypeChoices.EMAIL:
            try:
                _ = self.instance.email
            except EmailNotification.DoesNotExist:
                EmailNotification.objects.create(
                    notification=self.instance,
                    to_email_address=self.data.get('email')
                )
        elif self.instance.type == NotificationTypeChoices.SMS:
            try:
                sms_notification = self.instance.sms
            except SmsNotification.DoesNotExist:
                sms_notification = SmsNotification.objects.create(
                    notification=self.instance
                )

            sms_notification.to_phone_number = self.data.get('phone_number')
            if self.data.get('media_url'):
                sms_notification.media_url = self.data.get('media_url')
            sms_notification.save()

        elif self.instance.type == NotificationTypeChoices.PUSH:
            pass

        if self.instance.status == NotificationStatusChoices.SENT:
            self.instance.sent_datetime = localtime()

        super().save(commit=commit)

    class Meta:
        model = models.Notification
        exclude: ClassVar[list] = [
            'user', 'content_type', 'object_id', 'publish_datetime', 'content_object',
            'status_message'
        ]
