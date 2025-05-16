import os
import time
from collections import defaultdict

from django.utils.timezone import now
from twilio.rest.api.v2010.account.message import MessageInstance
from twilio.rest import Client

from django.conf import settings

from django_spire.notification.choices import NotificationStatusChoices
from django_spire.notification.models import Notification
from django_spire.notification.sms.consts import TWILIO_UNSUCCESSFUL_STATUSES
from django_spire.notification.sms.exceptions import TwilioException, \
    TwilioAPIConcurrentException

TWILIO_SMS_BATCH_SIZE = os.getenv('TWILIO_SMS_BATCH_SIZE')


class BulkTwilioSMSHelper:
    def __init__(self, notifications: list[Notification], client: Client):
        self.notifications = notifications
        self.client = client
        self.notification_segments = defaultdict(int)

    def _find_notification_segments(self):
        for notification in self.notifications:
            message = f'{notification.title}: {notification.body}'
            segments = len(message) // 160 + 1

            self.notification_segments[notification] = segments

    def send_notifications(self):
        self._find_notification_segments()

        sent_segments = 0
        for notification, segments in self.notification_segments.items():
            try:
                TwilioSMSHelper(notification, self.client).send()
                notification.status = NotificationStatusChoices.SENT
                notification.sent_datetime = now()

                sent_segments += segments

                if sent_segments >= TWILIO_SMS_BATCH_SIZE:
                    time.sleep(60)
                    sent_segments = 0

            except Exception as e:
                if isinstance(e, TwilioAPIConcurrentException):
                    notification.status = NotificationStatusChoices.PENDING

                if isinstance(e, TwilioException):
                    notification.status_message = str(e)
                    notification.status = NotificationStatusChoices.ERRORED
                    raise e

                else:
                    notification.status_message = str(e)
                    notification.status = NotificationStatusChoices.FAILED
                    raise e


class TwilioSMSHelper:
    def __init__(self, notification: Notification, client: Client):
        self.to_phone_number = self._format_phone_number(
            notification.sms.to_phone_number
        )
        self.message = f'{notification.title}: {notification.body}'
        self.client = client

    def _attempt_send(self) -> MessageInstance:
        try:
            return self.client.messages.create(
                to=self.to_phone_number,
                from_=settings.TWILIO_PHONE_NUMBER,
                body=self.message
            )
        except Exception as e:
            raise TwilioException(f'Twilio Exception: {str(e)}')

    def send(self):
        response = self._attempt_send()
        self._handle_response(response)

    def _handle_response(self, response: MessageInstance):
        if response.error_code == 429:
            raise TwilioAPIConcurrentException(
                'Twilio API concurrent request limit exceeded.'
            )
        if response.status in TWILIO_UNSUCCESSFUL_STATUSES:
            retry_response = self._attempt_send()

            if retry_response.status in TWILIO_UNSUCCESSFUL_STATUSES:
                raise TwilioException(
                    f'Twilio Exception: code={retry_response.error_code}, '
                    f'message={retry_response.error_message}'
                )

    @staticmethod
    def _format_phone_number(phone_number: str) -> str:
        cleaned_number = ''.join(filter(str.isdigit, phone_number))

        if len(cleaned_number) == 10:
            formatted_number = '1' + cleaned_number
        elif len(cleaned_number) == 11 and cleaned_number.startswith('1'):
            formatted_number = cleaned_number
        else:
            raise TwilioException(
                f'Invalid phone number format: {phone_number}.'
            )

        return '+' + formatted_number
