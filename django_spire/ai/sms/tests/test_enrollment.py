from __future__ import annotations

from unittest.mock import patch

from django.core.cache import cache
from django.urls import reverse

from django_spire.ai.sms.models import SmsCodePurposeChoices, SmsPhoneNumber
from django_spire.auth.user.models import AuthUser
from django_spire.core.tests.test_cases import BaseTestCase


MESSAGE_SEND_PATH = 'django_spire.ai.sms.views.enrollment_views.message_send'


class SmsEnrollmentTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

        cache.clear()

        self.confirm_url = reverse('django_spire:ai:sms:enrollment_confirm')
        self.session_code_url = reverse('django_spire:ai:sms:session_code')
        self.start_url = reverse('django_spire:ai:sms:enrollment_start')

    @patch(MESSAGE_SEND_PATH)
    def test_enrollment_start_creates_phone_number(self, mock_message_send) -> None:
        post_data = {'phone_number': '555-123-4567'}

        response = self.client.post(self.start_url, post_data)

        assert response.status_code == 200

        phone_number = SmsPhoneNumber.objects.get(phone_number='+15551234567')
        assert phone_number.user == self.super_user
        assert not phone_number.is_verified

        mock_message_send.assert_called_once()

        send_args = mock_message_send.call_args.args
        assert send_args[0] == '+15551234567'

    @patch(MESSAGE_SEND_PATH)
    def test_enrollment_start_rejects_invalid_phone_number(self, mock_message_send) -> None:
        post_data = {'phone_number': '12345'}

        response = self.client.post(self.start_url, post_data)

        assert response.status_code == 400
        mock_message_send.assert_not_called()

    @patch(MESSAGE_SEND_PATH)
    def test_enrollment_start_rejects_number_owned_by_other_user(self, mock_message_send) -> None:
        other_user = AuthUser.objects.create_user(username='other')

        SmsPhoneNumber.objects.create(
            user=other_user,
            phone_number='+15551234567',
            is_verified=True,
        )

        post_data = {'phone_number': '+15551234567'}

        response = self.client.post(self.start_url, post_data)

        assert response.status_code == 400
        mock_message_send.assert_not_called()

    def test_enrollment_confirm_verifies_phone_number(self) -> None:
        phone_number = SmsPhoneNumber.objects.create(
            user=self.super_user,
            phone_number='+15551234567',
        )

        code = phone_number.code_issue(SmsCodePurposeChoices.ENROLLMENT)

        post_data = {
            'code': code,
            'phone_number': '+15551234567',
        }

        response = self.client.post(self.confirm_url, post_data)

        assert response.status_code == 200

        phone_number.refresh_from_db()
        assert phone_number.is_verified
        assert phone_number.verified_datetime is not None

    def test_enrollment_confirm_rejects_wrong_code(self) -> None:
        phone_number = SmsPhoneNumber.objects.create(
            user=self.super_user,
            phone_number='+15551234567',
        )

        code = phone_number.code_issue(SmsCodePurposeChoices.ENROLLMENT)
        wrong_code = '000000' if code != '000000' else '111111'

        post_data = {
            'code': wrong_code,
            'phone_number': '+15551234567',
        }

        response = self.client.post(self.confirm_url, post_data)

        assert response.status_code == 400

        phone_number.refresh_from_db()
        assert not phone_number.is_verified

    def test_session_code_issued_for_verified_phone_number(self) -> None:
        phone_number = SmsPhoneNumber.objects.create(
            user=self.super_user,
            phone_number='+15551234567',
            is_verified=True,
        )

        post_data = {'phone_number': '+15551234567'}

        response = self.client.post(self.session_code_url, post_data)

        assert response.status_code == 200

        phone_number.refresh_from_db()

        code = response.json()['code']
        assert phone_number.code_confirm(code, SmsCodePurposeChoices.SESSION)

    def test_session_code_rejected_for_unverified_phone_number(self) -> None:
        SmsPhoneNumber.objects.create(
            user=self.super_user,
            phone_number='+15551234567',
        )

        post_data = {'phone_number': '+15551234567'}

        response = self.client.post(self.session_code_url, post_data)

        assert response.status_code == 404

    def test_enrollment_requires_login(self) -> None:
        self.client.logout()

        post_data = {'phone_number': '+15551234567'}

        response = self.client.post(self.start_url, post_data)

        assert response.status_code == 302
