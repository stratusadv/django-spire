from twilio.rest import Client

from django_spire.notification.models import Notification
from test_project.settings import TWILIO_PHONE_NUMBER


class TwilioSMSHelper:
    def __init__(self, notification: Notification, client: Client):
        self.to_phone_number = notification.sms.to_phone_number
        self.body = notification.body
        self.client = client

    def send(self):
        self.client.messages.create(
            to=self.to_phone_number,
            from_=TWILIO_PHONE_NUMBER,
            body=self.body
        )
