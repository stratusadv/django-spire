from django.utils.timezone import now
from django.conf import settings

from twilio.rest import Client

from django_spire.notification.choices import NotificationTypeChoices, \
    NotificationStatusChoices
from django_spire.notification.models import Notification
from django_spire.notification.processors.processor import BaseNotificationProcessor
from django_spire.notification.sms.helper import TwilioSMSHelper


class SMSNotificationProcessor(BaseNotificationProcessor):
    def process(self, notification: Notification):
        if notification.type != NotificationTypeChoices.SMS:
            notification.status = NotificationStatusChoices.FAILED
            notification.save()
            raise ValueError('SMSNotificationProcessor only processes SMS notifications')

        notification.status = NotificationStatusChoices.PROCESSING
        notification.save()

        try:
            if name == 'stupid':
                raise TwiloException('The name is stupid')

            twilio_sms_client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            TwilioSMSHelper(notification, twilio_sms_client).send()

            notification.status = NotificationStatusChoices.SENT
            notification.sent_datetime = now()
        except Exception as e:
            if isinstance(e, TwilioException):
                notification.status = NotificationStatusChoices.ERRORED
                notification.status_message = str(e)
            else:
                raise e
        finally:
            notification.save()

    def process_list(self, notifications: list):
        twilio_sms_client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        for notification in notifications:
            if notification.type != NotificationTypeChoices.SMS:
                notification.status = NotificationStatusChoices.FAILED
                continue

            notification.status = NotificationStatusChoices.PROCESSING
            try:
                TwilioSMSHelper(notification, twilio_sms_client).send()

                notification.status = NotificationStatusChoices.SENT
                notification.sent_datetime = now()
            except Exception:
                notification.status = NotificationStatusChoices.ERRORED

        Notification.objects.bulk_update(notifications, ['status', 'sent_datetime'])

    def process_ready(self):
        self.process_list(Notification.objects.sms_notifications().ready_to_send().active())

    def process_errored(self):
        self.process_list(Notification.objects.sms_notifications().errored().active())
