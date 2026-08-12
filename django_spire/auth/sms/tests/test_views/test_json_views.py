from __future__ import annotations

from unittest.mock import patch

from django.core.cache import cache
from django.test import override_settings
from django.urls import reverse

from django_spire.auth.sms.choices import AuthSmsCodePurposeChoices
from django_spire.auth.sms.models import AuthSms
from django_spire.auth.user.models import AuthUser
from django_spire.core.tests.test_cases import BaseTestCase

MESSAGE_SEND_PATH = 'django_spire.auth.sms.views.json_views.Client'

TWILIO_SETTINGS = {
    'TWILIO_ACCOUNT_SID': 'test-account-sid',
    'TWILIO_AUTH_TOKEN': 'test-auth-token',
    'TWILIO_PHONE_NUMBER': '+12025550123',
}


class AuthSmsVerificationTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

        cache.clear()

        self.confirm_url = reverse('django_spire:auth:sms:json:verification_confirm')
        self.session_code_url = reverse('django_spire:auth:sms:json:session_code')
        self.start_url = reverse('django_spire:auth:sms:json:verification_start')

    @override_settings(**TWILIO_SETTINGS)
    @patch(MESSAGE_SEND_PATH)
    def test_verification_start_creates_phone_number(self, mock_message_send) -> None:
        post_data = {'phone_number': '555-123-4567'}

        response = self.client.post(
            self.start_url, data=post_data, content_type='application/json'
        )

        assert response.status_code == 200
        assert response.json()['type'] == 'success'

        phone_number = AuthSms.objects.get(phone_number='+15551234567')
        assert phone_number.user == self.super_user
        assert not phone_number.is_verified

        mock_message_send.assert_called_once()

        create_call = mock_message_send.return_value.messages.create
        create_call.assert_called_once()
        assert create_call.call_args.kwargs['to'] == '+15551234567'

    @override_settings(**TWILIO_SETTINGS)
    @patch(MESSAGE_SEND_PATH)
    def test_verification_start_rejects_invalid_phone_number(self, mock_message_send) -> None:
        post_data = {'phone_number': '12345'}

        response = self.client.post(
            self.start_url, data=post_data, content_type='application/json'
        )

        assert response.status_code == 200
        assert response.json()['type'] == 'error'
        mock_message_send.assert_not_called()

    @override_settings(**TWILIO_SETTINGS)
    @patch(MESSAGE_SEND_PATH)
    def test_verification_start_rejects_number_owned_by_other_user(self, mock_message_send) -> None:
        other_user = AuthUser.objects.create_user(username='other')

        AuthSms.objects.create(user=other_user, phone_number='+15551234567', is_verified=True)

        post_data = {'phone_number': '+15551234567'}

        response = self.client.post(
            self.start_url, data=post_data, content_type='application/json'
        )

        assert response.status_code == 200
        assert response.json()['type'] == 'error'
        mock_message_send.assert_not_called()

    def test_verification_confirm_verifies_phone_number(self) -> None:
        phone_number = AuthSms.objects.create(user=self.super_user, phone_number='+15551234567')

        code = phone_number.services.processor.issue_code(AuthSmsCodePurposeChoices.VERIFICATION)

        post_data = {'code': code, 'phone_number': '+15551234567'}

        response = self.client.post(
            self.confirm_url, data=post_data, content_type='application/json'
        )

        assert response.status_code == 200

        phone_number.refresh_from_db()
        assert phone_number.is_verified
        assert phone_number.verified_datetime is not None

    @override_settings(**TWILIO_SETTINGS)
    @patch(MESSAGE_SEND_PATH)
    def test_verification_start_accepts_json_body(self, mock_message_send) -> None:
        post_data = {'phone_number': '555-123-4567'}

        response = self.client.post(self.start_url, data=post_data, content_type='application/json')

        assert response.status_code == 200

        phone_number = AuthSms.objects.get(phone_number='+15551234567')
        assert phone_number.user == self.super_user
        assert not phone_number.is_verified

        mock_message_send.assert_called_once()

    def test_verification_confirm_accepts_json_body(self) -> None:
        phone_number = AuthSms.objects.create(user=self.super_user, phone_number='+15551234567')

        code = phone_number.services.processor.issue_code(AuthSmsCodePurposeChoices.VERIFICATION)

        post_data = {'code': code, 'phone_number': '+15551234567'}

        response = self.client.post(
            self.confirm_url, data=post_data, content_type='application/json'
        )

        assert response.status_code == 200

        phone_number.refresh_from_db()
        assert phone_number.is_verified

    def test_verification_confirm_rejects_wrong_code(self) -> None:
        phone_number = AuthSms.objects.create(user=self.super_user, phone_number='+15551234567')

        code = phone_number.services.processor.issue_code(AuthSmsCodePurposeChoices.VERIFICATION)
        wrong_code = '000000' if code != '000000' else '111111'

        post_data = {'code': wrong_code, 'phone_number': '+15551234567'}

        response = self.client.post(
            self.confirm_url, data=post_data, content_type='application/json'
        )

        assert response.status_code == 200
        assert response.json()['type'] == 'error'

        phone_number.refresh_from_db()
        assert not phone_number.is_verified

    def test_session_code_issued_for_verified_phone_number(self) -> None:
        phone_number = AuthSms.objects.create(
            user=self.super_user, phone_number='+15551234567', is_verified=True
        )

        post_data = {'phone_number': '+15551234567'}

        response = self.client.post(
            self.session_code_url, data=post_data, content_type='application/json'
        )

        assert response.status_code == 200

        phone_number.refresh_from_db()

        code = response.json()['code']
        assert phone_number.services.processor.confirm_code(code, AuthSmsCodePurposeChoices.SESSION)

    def test_session_code_rejected_for_unverified_phone_number(self) -> None:
        AuthSms.objects.create(user=self.super_user, phone_number='+15551234567')

        post_data = {'phone_number': '+15551234567'}

        response = self.client.post(
            self.session_code_url, data=post_data, content_type='application/json'
        )

        assert response.status_code == 200
        assert response.json()['type'] == 'error'
        assert 'code' not in response.json()

    def test_verification_requires_login(self) -> None:
        self.client.logout()

        post_data = {'phone_number': '+15551234567'}

        response = self.client.post(self.start_url, post_data)

        assert response.status_code == 302
