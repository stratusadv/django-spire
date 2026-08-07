from __future__ import annotations

from datetime import timedelta

from django.utils.timezone import now

from django_spire.auth.sms.choices import SmsAuthCodePurposeChoices
from django_spire.auth.sms.models import SmsAuth
from django_spire.core.tests.test_cases import BaseTestCase


class SmsAuthModelTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

        self.phone_number = SmsAuth.objects.create(
            user=self.super_user,
            phone_number='+15551234567',
            is_verified=True,
        )

    def test_code_confirm_rejects_wrong_purpose(self) -> None:
        code = self.phone_number.services.code_issue(SmsAuthCodePurposeChoices.SESSION)

        assert not self.phone_number.services.code_confirm(
            code, SmsAuthCodePurposeChoices.ENROLLMENT
        )

    def test_code_confirm_is_single_use(self) -> None:
        code = self.phone_number.services.code_issue(SmsAuthCodePurposeChoices.SESSION)

        assert self.phone_number.services.code_confirm(code, SmsAuthCodePurposeChoices.SESSION)
        assert not self.phone_number.services.code_confirm(code, SmsAuthCodePurposeChoices.SESSION)

    def test_code_is_stored_hashed(self) -> None:
        code = self.phone_number.services.code_issue(SmsAuthCodePurposeChoices.SESSION)

        assert code not in self.phone_number.code_hash

    def test_code_issue_rejects_unknown_purpose(self) -> None:
        try:
            self.phone_number.services.code_issue('nonsense')
        except ValueError:
            return

        message = 'code_issue accepted an unknown purpose'
        raise AssertionError(message)

    def test_session_idle_expiry(self) -> None:
        self.phone_number.services.session_open()

        self.phone_number.session_last_activity_datetime = now() - timedelta(minutes=31)
        self.phone_number.save()

        assert not self.phone_number.services.session_is_active

    def test_session_duration_expiry(self) -> None:
        self.phone_number.services.session_open()

        self.phone_number.session_started_datetime = now() - timedelta(minutes=481)
        self.phone_number.save()

        assert not self.phone_number.services.session_is_active

    def test_session_close(self) -> None:
        self.phone_number.services.session_open()
        self.phone_number.services.session_close()

        assert not self.phone_number.services.session_is_active
