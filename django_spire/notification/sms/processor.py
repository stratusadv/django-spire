from __future__ import annotations

from django.utils.timezone import now
from django.conf import settings

from twilio.rest import Client

from django_spire.notification.choices import (
    NotificationTypeChoices,
    NotificationStatusChoices
)
from django_spire.notification.exceptions import InvalidNotificationTypeError
from django_spire.notification.models import Notification
from django_spire.notification.processors.processor import BaseNotificationProcessor
from django_spire.notification.sms.exceptions import (
    TwilioAPIConcurrentError,
    TwilioError
)
from django_spire.notification.sms.helper import TwilioSMSHelper, BulkTwilioSMSHelper


class SMSNotificationProcessor(BaseNotificationProcessor):
    def _validate_notification_type(self, notification: Notification):
        if notification.type != NotificationTypeChoices.SMS:
            raise InvalidNotificationTypeError(NotificationTypeChoices.SMS, notification.type)

    def process(self, notification: Notification):
        notification.status = NotificationStatusChoices.PROCESSING
        notification.save()

        try:
            self._validate_notification_type(notification)

            twilio_sms_client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            TwilioSMSHelper(notification, twilio_sms_client).send()

            notification.status = NotificationStatusChoices.SENT
            notification.sent_datetime = now()
        except Exception as e:
            if isinstance(e, TwilioAPIConcurrentError):
                notification.status = NotificationStatusChoices.PENDING
                notification.save()
                return

            notification.status_message = str(e)

            if isinstance(e, TwilioError):
                notification.status = NotificationStatusChoices.ERRORED
            else:
                notification.status = NotificationStatusChoices.FAILED
                raise
        finally:
            notification.save()

    def process_list(self, notifications: list):
        twilio_sms_client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

        for notification in notifications:
            self._validate_notification_type(notification)

        try:
            BulkTwilioSMSHelper(notifications, twilio_sms_client).send_notifications()
        finally:
            Notification.objects.bulk_update(
                notifications,
                ['status', 'sent_datetime', 'status_message']
            )

    def process_ready(self):
        self.process_list(Notification.objects.sms_notifications().ready_to_send().active())

    def process_errored(self):
        self.process_list(Notification.objects.sms_notifications().errored().active())
