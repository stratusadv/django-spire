from django.utils.timezone import now
from django.conf import settings

from twilio.rest import Client

from django_spire.notification.choices import NotificationTypeChoices, \
    NotificationStatusChoices
from django_spire.notification.exceptions import NotificationException
from django_spire.notification.models import Notification
from django_spire.notification.processors.processor import BaseNotificationProcessor
from django_spire.notification.sms.exceptions import TwilioException, \
    TwilioAPIConcurrentException
from django_spire.notification.sms.helper import TwilioSMSHelper, BulkTwilioSMSHelper


class SMSNotificationProcessor(BaseNotificationProcessor):
    def process(self, notification: Notification):
        notification.status = NotificationStatusChoices.PROCESSING
        notification.save()

        try:
            if notification.type != NotificationTypeChoices.SMS:
                raise NotificationException(
                    f'SMSNotificationProcessor only processes '
                    f'SMS notifications. Was provided {notification.type}'
                )

            twilio_sms_client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            TwilioSMSHelper(notification, twilio_sms_client).send()

            notification.status = NotificationStatusChoices.SENT
            notification.sent_datetime = now()
        except Exception as e:
            # Requeue notification as api concurrency is full
            if isinstance(e, TwilioAPIConcurrentException):
                notification.status = NotificationStatusChoices.PENDING
                notification.save()
                return

            notification.status_message = str(e)

            if isinstance(e, TwilioException):
                notification.status = NotificationStatusChoices.ERRORED
            else:
                notification.status = NotificationStatusChoices.FAILED
                raise e
        finally:
            notification.save()

    def process_list(self, notifications: list):
        twilio_sms_client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        for notification in notifications:
            if notification.type != NotificationTypeChoices.SMS:
                raise NotificationException(
                    f'SMSNotificationProcessor only processes '
                    f'SMS notifications. Was provided {notification.type}'
                )

        try:
            BulkTwilioSMSHelper(notifications, twilio_sms_client).send_notifications()
        except Exception as e:
            raise e
        finally:
            Notification.objects.bulk_update(
                notifications,
                ['status', 'sent_datetime', 'status_message']
            )

    def process_ready(self):
        self.process_list(Notification.objects.sms_notifications().ready_to_send().active())

    def process_errored(self):
        self.process_list(Notification.objects.sms_notifications().errored().active())
