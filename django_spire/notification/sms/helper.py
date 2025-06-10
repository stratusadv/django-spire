import base64
import time
import uuid
from datetime import timedelta

import requests
from collections import defaultdict

from django.utils.timezone import now
from html2image import Html2Image
from twilio.rest.api.v2010.account.message import MessageInstance
from twilio.rest import Client

from django.conf import settings

from django_spire.notification.choices import NotificationStatusChoices
from django_spire.notification.models import Notification
from django_spire.notification.sms.choices import SmsMediaTypeChoices
from django_spire.notification.sms.constants import SMS_TEMPORARY_MEDIA_TYPES_MAP
from django_spire.notification.sms.consts import TWILIO_UNSUCCESSFUL_STATUSES
from django_spire.notification.sms.exceptions import TwilioException, \
    TwilioAPIConcurrentException
from django_spire.notification.sms.models import SmsTemporaryMedia


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

                if sent_segments >= settings.TWILIO_SMS_BATCH_SIZE:
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
        self.notification = notification
        self.message = f'{notification.title}: {notification.body}'
        self.client = client

    def _attempt_send(self) -> MessageInstance:
        try:
            media_url = SmsMediaHelper(notification=self.notification).generate_media()
            return self.client.messages.create(
                to=self.to_phone_number,
                from_=settings.TWILIO_PHONE_NUMBER,
                body=self.message,
                media_url=[media_url] if media_url else [],
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


class SmsMediaHelper:
    def __init__(self, notification: Notification):
        self.content = ''
        self.external_url = ''
        self.media_type = ''
        self.media_url = notification.sms.media_url
        self.notification = notification
        self.temp_file = ''

    def generate_media(self) -> str:
        self.media_type = self._retrieve_content_type()

        if self.media_type == SmsMediaTypeChoices.PNG:
            self._generate_png()
            self._save_content()

            return self.external_url
        else:
            raise TwilioException(
                f'Unsupported content type for SMS template: {self.media_type}'
            )

    def _generate_png(self):
        hti = Html2Image(custom_flags=['--hide-scrollbars', '--window-position=0,0'])
        hti.screenshot(url=self.media_url, save_as='temp.png')
        self.temp_file = 'temp.png'

    def _retrieve_content_type(self):
        try:
            response = requests.head(self.media_url)
            response.raise_for_status()
            content_type = response.headers.get('Content-Type', '').lower()

            if content_type not in SMS_TEMPORARY_MEDIA_TYPES_MAP.keys():
                raise TwilioException(
                    f'Unsupported content type for SMS template: {content_type}'
                )

            return SMS_TEMPORARY_MEDIA_TYPES_MAP[content_type]

        except requests.RequestException as e:
            raise TwilioException(f'Error fetching {self.media_url}: {e}')

    def _save_content(self):
        with open(self.temp_file, 'rb') as f:
            self.content = base64.b64encode(f.read()).decode('utf-8')
        f.close()

        temporary_media = SmsTemporaryMedia.objects.create(
            name=self.media_url,
            content_type=self.media_type,
            content=self.content,
            expire_datetime=now() + timedelta(days=1), # TODO: make configurable
            external_access_key=uuid.uuid4(),
        )

        self.external_url = '' # TODO: Set this to be an actual URL
        temporary_media.external_url = self.external_url
        temporary_media.save()

        self.notification.sms.temporary_media = temporary_media
        self.notification.sms.save()
