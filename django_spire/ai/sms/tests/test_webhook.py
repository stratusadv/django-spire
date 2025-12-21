from __future__ import annotations

from unittest.mock import patch

from django.urls import reverse

from django_spire.ai.sms.models import SmsConversation
from django_spire.core.tests.test_cases import BaseTestCase


class SmsWebhookTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

        self.webhook_url = reverse('django_spire:ai:sms:webhook')

    @patch('twilio.request_validator.RequestValidator.validate')
    def test_webhook_receives_message(self, mock_validate) -> None:
        mock_validate.return_value = True

        response = self.client.post(
            self.webhook_url,
            {
                'From': '+15551234567',
                'Body': 'Hello',
                'MessageSid': 'SM123456789'
            }
        )

        assert response.status_code == 200

        conversation = SmsConversation.objects.get(phone_number='+15551234567')
        assert conversation.messages.count() == 2

        inbound_message = conversation.messages.filter(is_inbound=True).first()
        assert inbound_message.body == 'Hello'
        assert inbound_message.twilio_sid == 'SM123456789'

        outbound_message = conversation.messages.filter(is_inbound=False).first()
        assert len(outbound_message.body) > 0

    @patch('twilio.request_validator.RequestValidator.validate')
    def test_webhook_creates_conversation(self, mock_validate) -> None:
        mock_validate.return_value = True

        initial_count = SmsConversation.objects.count()

        self.client.post(
            self.webhook_url,
            {
                'From': '+15559999999',
                'Body': 'New conversation',
                'MessageSid': 'SM999999999'
            }
        )

        assert SmsConversation.objects.count() == initial_count + 1

    @patch('twilio.request_validator.RequestValidator.validate')
    def test_webhook_reuses_existing_conversation(self, mock_validate) -> None:
        mock_validate.return_value = True

        SmsConversation.objects.create(phone_number='+15551234567')

        initial_count = SmsConversation.objects.count()

        self.client.post(
            self.webhook_url,
            {
                'From': '+15551234567',
                'Body': 'Another message',
                'MessageSid': 'SM123456789'
            }
        )

        assert SmsConversation.objects.count() == initial_count

    @patch('twilio.request_validator.RequestValidator.validate')
    def test_webhook_invalid_signature(self, mock_validate) -> None:
        mock_validate.return_value = False

        response = self.client.post(
            self.webhook_url,
            {
                'From': '+15551234567',
                'Body': 'Hello',
                'MessageSid': 'SM123456789'
            }
        )

        assert response.status_code == 403

    @patch('twilio.request_validator.RequestValidator.validate')
    def test_webhook_short_phone_number(self, mock_validate) -> None:
        mock_validate.return_value = True

        response = self.client.post(
            self.webhook_url,
            {
                'From': '1234',
                'Body': 'Hello',
                'MessageSid': 'SM123456789'
            }
        )

        assert response.status_code == 403

    @patch('twilio.request_validator.RequestValidator.validate')
    def test_webhook_empty_body(self, mock_validate) -> None:
        mock_validate.return_value = True

        response = self.client.post(
            self.webhook_url,
            {
                'From': '+15551234567',
                'Body': '',
                'MessageSid': 'SM123456789'
            }
        )

        assert response.status_code == 200

    @patch('twilio.request_validator.RequestValidator.validate')
    def test_webhook_marks_inbound_as_processed(self, mock_validate) -> None:
        mock_validate.return_value = True

        self.client.post(
            self.webhook_url,
            {
                'From': '+15551234567',
                'Body': 'Test message',
                'MessageSid': 'SM123456789'
            }
        )

        conversation = SmsConversation.objects.get(phone_number='+15551234567')
        inbound_message = conversation.messages.filter(is_inbound=True).first()

        assert inbound_message.is_processed

    @patch('twilio.request_validator.RequestValidator.validate')
    def test_webhook_response_is_twiml(self, mock_validate) -> None:
        mock_validate.return_value = True

        response = self.client.post(
            self.webhook_url,
            {
                'From': '+15551234567',
                'Body': 'Hello',
                'MessageSid': 'SM123456789'
            }
        )

        assert b'<Response>' in response.content or b'Response' in response.content

    @patch('twilio.request_validator.RequestValidator.validate')
    def test_webhook_missing_from(self, mock_validate) -> None:
        mock_validate.return_value = True

        response = self.client.post(
            self.webhook_url,
            {
                'Body': 'Hello',
                'MessageSid': 'SM123456789'
            }
        )

        assert response.status_code == 403

    @patch('twilio.request_validator.RequestValidator.validate')
    def test_webhook_stores_twilio_sid(self, mock_validate) -> None:
        mock_validate.return_value = True

        self.client.post(
            self.webhook_url,
            {
                'From': '+15551234567',
                'Body': 'Hello',
                'MessageSid': 'SM_TEST_SID_123'
            }
        )

        conversation = SmsConversation.objects.get(phone_number='+15551234567')
        inbound_message = conversation.messages.filter(is_inbound=True).first()

        assert inbound_message.twilio_sid == 'SM_TEST_SID_123'
