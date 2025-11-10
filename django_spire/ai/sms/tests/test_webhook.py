from unittest.mock import patch

from django.urls import reverse

from django_spire.ai.sms.models import SmsConversation
from django_spire.core.tests.test_cases import BaseTestCase


class SmsWebhookTests(BaseTestCase):
    def setUp(self):
        super().setUp()

        self.webhook_url = reverse('django_spire:ai:sms:webhook')

    @patch('twilio.request_validator.RequestValidator.validate')
    def test_webhook_receives_message(self, mock_validate):
        mock_validate.return_value = True

        response = self.client.post(
            self.webhook_url,
            {
                'From': '+15551234567',
                'Body': 'Hello',
                'MessageSid': 'SM123456789'
            }
        )

        self.assertEqual(response.status_code, 200)

        conversation = SmsConversation.objects.get(phone_number='+15551234567')
        self.assertEqual(conversation.messages.count(), 2)  # Inbound and outbound

        inbound_message = conversation.messages.filter(is_inbound=True).first()
        self.assertEqual(inbound_message.body, 'Hello')
        self.assertEqual(inbound_message.twilio_sid, 'SM123456789')

        outbound_message = conversation.messages.filter(is_inbound=False).first()
        self.assertTrue(len(outbound_message.body) > 0)
