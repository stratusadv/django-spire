from twilio.rest import Client

from django_spire.notification.models import Notification
from django.conf import settings


class TwilioSMSHelper:
    def __init__(self, notification: Notification, client: Client):
        self.to_phone_number = notification.sms.to_phone_number
        self.message = f'{notification.title}: {notification.body}'
        self.client = client

    def send(self):
        self.client.messages.create(
            to='+' + self.to_phone_number,
            from_=settings.TWILIO_PHONE_NUMBER,
            body=self.message
        )
