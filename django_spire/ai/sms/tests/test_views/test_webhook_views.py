from __future__ import annotations

from datetime import timedelta
from unittest.mock import patch

from django.core.cache import cache
from django.test import override_settings
from django.urls import reverse
from django.utils.timezone import now

from django_spire.ai.sms.intelligence.intel import SmsIntel
from django_spire.ai.sms.models import SmsConversation
from django_spire.auth.sms.choices import AuthSmsCodePurposeChoices
from django_spire.auth.sms.models import AuthSms
from django_spire.core.tests.test_cases import BaseTestCase

WORKFLOW_PATH = 'django_spire.ai.sms.views.webhook_views.sms_conversation_workflow'


@override_settings(TWILIO_AUTH_TOKEN='twilio-test-token')
class SmsWebhookTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

        cache.clear()

        self.webhook_url = reverse('django_spire:ai:sms:webhook')

        self.phone_number = AuthSms.objects.create(
            user=self.super_user,
            phone_number='+15551234567',
            is_verified=True,
        )

        self.phone_number.services.processor.open_session()

    def _post_webhook(self, body: str, from_number: str = '+15551234567', sid: str = 'SM123456789'):
        post_data = {
            'From': from_number,
            'Body': body,
            'MessageSid': sid,
        }

        return self.client.post(self.webhook_url, post_data)

    @patch(WORKFLOW_PATH)
    @patch('twilio.request_validator.RequestValidator.validate')
    def test_webhook_receives_message(self, mock_validate, mock_workflow) -> None:
        mock_validate.return_value = True
        mock_workflow.return_value = SmsIntel(body='Answer')

        response = self._post_webhook('Hello')

        assert response.status_code == 200
        assert b'<Response>' in response.content
        assert b'Answer' in response.content

        conversation = SmsConversation.objects.get(phone_number='+15551234567')
        assert conversation.user == self.super_user
        assert conversation.messages.count() == 2

        inbound_message = conversation.messages.filter(is_inbound=True).first()
        assert inbound_message.body == 'Hello'
        assert inbound_message.twilio_sid == 'SM123456789'
        assert inbound_message.is_processed

    @patch(WORKFLOW_PATH)
    @patch('twilio.request_validator.RequestValidator.validate')
    def test_webhook_unregistered_number_is_silent(self, mock_validate, mock_workflow) -> None:
        mock_validate.return_value = True

        response = self._post_webhook('Hello', from_number='+15559999999', sid='SM999')

        assert response.status_code == 200
        assert b'<Message>' not in response.content
        assert SmsConversation.objects.filter(phone_number='+15559999999').count() == 0
        mock_workflow.assert_not_called()

    @patch(WORKFLOW_PATH)
    @patch('twilio.request_validator.RequestValidator.validate')
    def test_webhook_unverified_number_is_silent(self, mock_validate, mock_workflow) -> None:
        mock_validate.return_value = True

        AuthSms.objects.create(
            user=self.super_user,
            phone_number='+15558888888',
            is_verified=False,
        )

        response = self._post_webhook('Hello', from_number='+15558888888', sid='SM888')

        assert response.status_code == 200
        assert b'<Message>' not in response.content
        mock_workflow.assert_not_called()

    @patch(WORKFLOW_PATH)
    @patch('twilio.request_validator.RequestValidator.validate')
    def test_webhook_locked_session_prompts_unlock(self, mock_validate, mock_workflow) -> None:
        mock_validate.return_value = True

        self.phone_number.services.processor.close_session()

        response = self._post_webhook('What is our Q3 revenue?')

        assert response.status_code == 200
        assert b'<Response>' in response.content
        assert b'locked' in response.content
        assert SmsConversation.objects.filter(phone_number='+15551234567').count() == 0
        mock_workflow.assert_not_called()

    @patch('twilio.request_validator.RequestValidator.validate')
    def test_webhook_unlock_code_opens_session(self, mock_validate) -> None:
        mock_validate.return_value = True

        self.phone_number.services.processor.close_session()

        code = self.phone_number.services.processor.issue_code(AuthSmsCodePurposeChoices.SESSION)

        response = self._post_webhook(code)

        assert response.status_code == 200
        assert b'<Response>' in response.content
        assert b'unlocked' in response.content

        self.phone_number.refresh_from_db()
        assert self.phone_number.session_is_active

    @patch('twilio.request_validator.RequestValidator.validate')
    def test_webhook_wrong_code_stays_locked(self, mock_validate) -> None:
        mock_validate.return_value = True

        self.phone_number.services.processor.close_session()

        code = self.phone_number.services.processor.issue_code(AuthSmsCodePurposeChoices.SESSION)
        wrong_code = '000000' if code != '000000' else '111111'

        response = self._post_webhook(wrong_code)

        assert response.status_code == 200
        assert b'<Response>' in response.content
        assert b'locked' in response.content

        self.phone_number.refresh_from_db()
        assert not self.phone_number.session_is_active
        assert self.phone_number.code_attempt_count == 1

    @patch('twilio.request_validator.RequestValidator.validate')
    def test_webhook_expired_code_stays_locked(self, mock_validate) -> None:
        mock_validate.return_value = True

        self.phone_number.services.processor.close_session()

        code = self.phone_number.services.processor.issue_code(AuthSmsCodePurposeChoices.SESSION)

        self.phone_number.code_expiration_datetime = now() - timedelta(minutes=1)
        self.phone_number.save()

        response = self._post_webhook(code)

        assert response.status_code == 200
        assert b'locked' in response.content

        self.phone_number.refresh_from_db()
        assert not self.phone_number.session_is_active

    @patch('twilio.request_validator.RequestValidator.validate')
    def test_webhook_attempt_limit_blocks_code(self, mock_validate) -> None:
        mock_validate.return_value = True

        self.phone_number.services.processor.close_session()

        code = self.phone_number.services.processor.issue_code(AuthSmsCodePurposeChoices.SESSION)

        self.phone_number.code_attempt_count = 5
        self.phone_number.save()

        response = self._post_webhook(code)

        assert response.status_code == 200
        assert b'locked' in response.content

    @patch(WORKFLOW_PATH)
    @patch('twilio.request_validator.RequestValidator.validate')
    def test_webhook_duplicate_sid_is_ignored(self, mock_validate, mock_workflow) -> None:
        mock_validate.return_value = True
        mock_workflow.return_value = SmsIntel(body='Answer')

        self._post_webhook('Hello', sid='SM_DUPLICATE')
        self._post_webhook('Hello', sid='SM_DUPLICATE')

        conversation = SmsConversation.objects.get(phone_number='+15551234567')
        assert conversation.messages.count() == 2
        assert mock_workflow.call_count == 1

    @override_settings(DJANGO_SPIRE_AUTH_SMS_THROTTLE_RATE_PER_MINUTE=1)
    @patch(WORKFLOW_PATH)
    @patch('twilio.request_validator.RequestValidator.validate')
    def test_webhook_throttle_drops_excess_messages(self, mock_validate, mock_workflow) -> None:
        mock_validate.return_value = True
        mock_workflow.return_value = SmsIntel(body='Answer')

        self._post_webhook('First', sid='SM_THROTTLE_1')
        self._post_webhook('Second', sid='SM_THROTTLE_2')

        conversation = SmsConversation.objects.get(phone_number='+15551234567')
        assert conversation.messages.count() == 2
        assert mock_workflow.call_count == 1

    @override_settings(DJANGO_SPIRE_AI_SMS_BODY_LENGTH_MAX=10)
    @patch(WORKFLOW_PATH)
    @patch('twilio.request_validator.RequestValidator.validate')
    def test_webhook_oversized_body_is_rejected(self, mock_validate, mock_workflow) -> None:
        mock_validate.return_value = True

        response = self._post_webhook('This message is longer than ten characters')

        assert response.status_code == 200
        assert b'too long' in response.content
        mock_workflow.assert_not_called()

    @patch('twilio.request_validator.RequestValidator.validate')
    def test_webhook_invalid_signature(self, mock_validate) -> None:
        mock_validate.return_value = False

        response = self._post_webhook('Hello')

        assert response.status_code == 403

    @override_settings(TWILIO_AUTH_TOKEN=None)
    @patch.dict('os.environ', {'TWILIO_AUTH_TOKEN': ''})
    @patch('twilio.request_validator.RequestValidator.validate')
    def test_webhook_missing_token_is_forbidden(self, mock_validate) -> None:
        mock_validate.return_value = True

        response = self._post_webhook('Hello')

        assert response.status_code == 403
        mock_validate.assert_not_called()

    @patch('twilio.request_validator.RequestValidator.validate')
    def test_webhook_short_phone_number(self, mock_validate) -> None:
        mock_validate.return_value = True

        response = self._post_webhook('Hello', from_number='1234')

        assert response.status_code == 403

    @patch('twilio.request_validator.RequestValidator.validate')
    def test_webhook_missing_from(self, mock_validate) -> None:
        mock_validate.return_value = True

        post_data = {
            'Body': 'Hello',
            'MessageSid': 'SM123456789',
        }

        response = self.client.post(self.webhook_url, post_data)

        assert response.status_code == 403

    @patch(WORKFLOW_PATH)
    @patch('twilio.request_validator.RequestValidator.validate')
    def test_webhook_knowledge_path(self, mock_validate, mock_workflow) -> None:
        mock_validate.return_value = True
        mock_workflow.return_value = SmsIntel(body='Knowledge search result')

        response = self._post_webhook('Tell me about documentation')

        assert response.status_code == 200
        mock_workflow.assert_called_once()

        conversation = SmsConversation.objects.get(phone_number='+15551234567')
        assert conversation.messages.count() == 2

        inbound_message = conversation.messages.filter(is_inbound=True).first()
        assert inbound_message.is_processed

        outbound_message = conversation.messages.filter(is_inbound=False).first()
        assert outbound_message.body == 'Knowledge search result'

        assert b'Knowledge search result' in response.content

