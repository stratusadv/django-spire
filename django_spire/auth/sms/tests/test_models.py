from __future__ import annotations

from datetime import timedelta

from django.core.cache import cache
from django.utils.timezone import now

from django_spire.auth.sms.choices import AuthSmsCodePurposeChoices
from django_spire.auth.sms.models import AuthSms
from django_spire.conf import settings
from django_spire.core.tests.test_cases import BaseTestCase


class AuthSmsModelTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

        cache.clear()

        self.phone_number = AuthSms.objects.create(
            user=self.super_user,
            phone_number='+15551234567',
            is_verified=True,
        )

    def test_code_confirm_rejects_wrong_purpose(self) -> None:
        code = self.phone_number.services.processor.issue_code(AuthSmsCodePurposeChoices.SESSION)

        assert not self.phone_number.services.processor.confirm_code(
            code, AuthSmsCodePurposeChoices.VERIFICATION
        )

    def test_code_confirm_is_single_use(self) -> None:
        code = self.phone_number.services.processor.issue_code(AuthSmsCodePurposeChoices.SESSION)

        assert self.phone_number.services.processor.confirm_code(
            code, AuthSmsCodePurposeChoices.SESSION
        )
        assert not self.phone_number.services.processor.confirm_code(
            code, AuthSmsCodePurposeChoices.SESSION
        )

    def test_code_is_stored_hashed(self) -> None:
        code = self.phone_number.services.processor.issue_code(AuthSmsCodePurposeChoices.SESSION)

        assert code not in self.phone_number.code_hash

    def test_code_issue_rejects_unknown_purpose(self) -> None:
        try:
            self.phone_number.services.processor.issue_code('nonsense')
        except ValueError:
            return

        message = 'issue_code accepted an unknown purpose'
        raise AssertionError(message)

    def test_session_idle_expiry(self) -> None:
        self.phone_number.services.processor.open_session()

        self.phone_number.session_last_activity_datetime = now() - timedelta(minutes=31)
        self.phone_number.save()

        assert not self.phone_number.session_is_active

    def test_session_duration_expiry(self) -> None:
        self.phone_number.services.processor.open_session()

        self.phone_number.session_started_datetime = now() - timedelta(minutes=481)
        self.phone_number.save()

        assert not self.phone_number.session_is_active

    def test_session_close(self) -> None:
        self.phone_number.services.processor.open_session()
        self.phone_number.services.processor.close_session()

        assert not self.phone_number.session_is_active

    def test_not_throttled_below_minute_limit(self) -> None:
        self.phone_number.record_attempt()

        assert not self.phone_number.is_throttled()

    def test_throttled_when_minute_limit_exceeded(self) -> None:
        rate_max = settings.DJANGO_SPIRE_AUTH_SMS_THROTTLE_RATE_PER_MINUTE

        for _ in range(rate_max + 1):
            self.phone_number.record_attempt()

        assert self.phone_number.is_throttled()

    def test_is_throttled_is_read_only(self) -> None:
        rate_max = settings.DJANGO_SPIRE_AUTH_SMS_THROTTLE_RATE_PER_MINUTE

        for _ in range(rate_max):
            self.phone_number.record_attempt()

        assert not self.phone_number.is_throttled()
        assert not self.phone_number.is_throttled()
