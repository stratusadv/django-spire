from __future__ import annotations

from datetime import timedelta

from django.utils import timezone

from django_spire.auth.sms.choices import AuthSmsCodePurposeChoices
from django_spire.auth.sms.models import AuthSms
from django_spire.core.tests.test_cases import BaseTestCase


class AuthSmsProcessorTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

        self.phone_number = AuthSms.objects.create(
            user=self.super_user, phone_number='+15551234567', is_verified=True
        )

    def test_open_session_stores_aware_datetimes(self) -> None:
        with timezone.override('Pacific/Kiritimati'):
            self.phone_number.services.processor.open_session()

        self.phone_number.refresh_from_db()

        assert timezone.is_aware(self.phone_number.session_started_datetime)
        assert timezone.is_aware(self.phone_number.session_last_activity_datetime)
        assert (
            self.phone_number.session_started_datetime
            == self.phone_number.session_last_activity_datetime
        )

    def test_touch_session_stores_aware_activity_datetime(self) -> None:
        self.phone_number.services.processor.open_session()

        with timezone.override('Pacific/Pago_Pago'):
            self.phone_number.services.processor.touch_session()

        self.phone_number.refresh_from_db()

        assert timezone.is_aware(self.phone_number.session_last_activity_datetime)
        assert (
            self.phone_number.session_last_activity_datetime
            >= self.phone_number.session_started_datetime
        )

    def test_issue_code_expiration_is_aware_and_in_future(self) -> None:
        with timezone.override('Pacific/Kiritimati'):
            self.phone_number.services.processor.issue_code(AuthSmsCodePurposeChoices.SESSION)

        self.phone_number.refresh_from_db()

        assert timezone.is_aware(self.phone_number.code_expiration_datetime)
        assert self.phone_number.code_expiration_datetime > timezone.now()

    def test_confirm_code_succeeds_within_window_outside_active_zone(self) -> None:
        code = self.phone_number.services.processor.issue_code(AuthSmsCodePurposeChoices.SESSION)

        with timezone.override('Pacific/Pago_Pago'):
            assert self.phone_number.services.processor.confirm_code(
                code, AuthSmsCodePurposeChoices.SESSION
            )

    def test_confirm_code_expired_outside_active_zone(self) -> None:
        self.phone_number.services.processor.issue_code(AuthSmsCodePurposeChoices.SESSION)

        with timezone.override('Pacific/Kiritimati'):
            self.phone_number.code_expiration_datetime = timezone.localtime(
                timezone.now() - timedelta(minutes=1)
            )
            self.phone_number.save()

        assert not self.phone_number.services.processor.confirm_code(
            '000000', AuthSmsCodePurposeChoices.SESSION
        )

        self.phone_number.refresh_from_db()

        assert self.phone_number.code_hash == ''
        assert self.phone_number.code_expiration_datetime is None

    def test_session_activity_boundary_survives_zone_shift(self) -> None:
        self.phone_number.services.processor.open_session()

        with timezone.override('Pacific/Kiritimati'):
            self.phone_number.session_last_activity_datetime = timezone.now() - timedelta(
                minutes=31
            )
            self.phone_number.save()

            assert not self.phone_number.session_is_active

    def test_session_activity_within_window_survives_zone_shift(self) -> None:
        self.phone_number.services.processor.open_session()

        with timezone.override('Pacific/Pago_Pago'):
            self.phone_number.session_last_activity_datetime = timezone.now() - timedelta(
                minutes=29
            )
            self.phone_number.save()

            assert self.phone_number.session_is_active

    def test_mark_verified_stores_aware_datetime(self) -> None:
        with timezone.override('Pacific/Kiritimati'):
            self.phone_number.services.processor.mark_verified()

        self.phone_number.refresh_from_db()

        assert timezone.is_aware(self.phone_number.verified_datetime)
