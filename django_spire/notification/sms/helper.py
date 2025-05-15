from twilio.rest.api.v2010.account.message import MessageInstance
from twilio.rest import Client

from django.conf import settings

from django_spire.notification.models import Notification
from django_spire.notification.sms.consts import TWILIO_UNSUCCESSFUL_STATUSES
from django_spire.notification.sms.exceptions import TwilioException


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
