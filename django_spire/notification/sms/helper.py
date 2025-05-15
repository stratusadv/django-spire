from twilio.rest.api.v2010.account.message import MessageInstance
from twilio.rest import Client

from django.conf import settings

from django_spire.notification.models import Notification
from django_spire.notification.sms.consts import TWILIO_UNSUCCESSFUL_STATUSES
from django_spire.notification.sms.exceptions import TwilioException


class TwilioSMSHelper:
    def __init__(self, notification: Notification, client: Client):
        self.to_phone_number = notification.sms.to_phone_number
        self.message = f'{notification.title}: {notification.body}'
        self.client = client

    def _attempt_send(self) -> MessageInstance:
        try:
            return self.client.messages.create(
                to='+' + self.to_phone_number,
                from_=settings.TWILIO_PHONE_NUMBER,
                body=self.message
            )
        except Exception as e:
            raise TwilioException(f'Twilio Exception: {str(e)}')

    def send(self):
        response = self._attempt_send()
        self._handle_response(response)

    def _handle_response(self, response: MessageInstance):
        if response.status in TWILIO_UNSUCCESSFUL_STATUSES:
            retry_response = self._attempt_send()

            if retry_response.status in TWILIO_UNSUCCESSFUL_STATUSES:
                raise TwilioException(
                    f'Twilio Exception: code={retry_response.error_code}, '
                    f'message={retry_response.error_message}'
                )
