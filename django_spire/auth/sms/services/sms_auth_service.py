from __future__ import annotations

import secrets
from datetime import timedelta
from typing import TYPE_CHECKING

from django.contrib.auth.hashers import check_password, make_password
from django.utils.timezone import now

from django_spire.auth.sms.choices import SmsAuthCodePurposeChoices
from django_spire.auth.sms.constants import CODE_DIGIT_COUNT
from django_spire.conf import settings
from django_spire.contrib.constructor.service import BaseDjangoModelService

if TYPE_CHECKING:
    from django_spire.auth.sms.models import SmsAuth


class SmsAuthService(BaseDjangoModelService['SmsAuth']):
    obj: SmsAuth

    def code_clear(self) -> None:
        self.obj.code_hash = ''
        self.obj.code_purpose = ''
        self.obj.code_expiration_datetime = None
        self.obj.code_attempt_count = 0
        self.obj.save()

    def code_confirm(self, code: str, purpose: str) -> bool:
        if (
            self.obj.code_hash == ''
            or self.obj.code_purpose != purpose
            or self.obj.code_expiration_datetime is None
        ):
            return False

        if now() > self.obj.code_expiration_datetime:
            self.code_clear()
            return False

        attempt_count_max = settings.DJANGO_SPIRE_AUTH_SMS_CODE_ATTEMPT_COUNT_MAX

        if self.obj.code_attempt_count >= attempt_count_max:
            self.code_clear()
            return False

        if not check_password(code, self.obj.code_hash):
            self.obj.code_attempt_count += 1
            self.obj.save()
            return False

        self.code_clear()

        return True

    def code_issue(self, purpose: str) -> str:
        if purpose not in SmsAuthCodePurposeChoices.values:
            message = f'unknown sms auth purpose: {purpose}'
            raise ValueError(message)

        code = f'{secrets.randbelow(10 ** CODE_DIGIT_COUNT):0{CODE_DIGIT_COUNT}d}'
        expiry_minutes = settings.DJANGO_SPIRE_AUTH_SMS_CODE_EXPIRY_MINUTES

        self.obj.code_hash = make_password(code)
        self.obj.code_purpose = purpose
        self.obj.code_expiration_datetime = now() + timedelta(minutes=expiry_minutes)
        self.obj.code_attempt_count = 0
        self.obj.save()

        return code

    def session_close(self) -> None:
        self.obj.session_started_datetime = None
        self.obj.session_last_activity_datetime = None
        self.obj.save()

    @property
    def session_is_active(self) -> bool:
        if self.obj.session_started_datetime is None:
            return False

        if self.obj.session_last_activity_datetime is None:
            return False

        duration_minutes_max = settings.DJANGO_SPIRE_AUTH_SMS_SESSION_DURATION_MINUTES_MAX
        idle_minutes_max = settings.DJANGO_SPIRE_AUTH_SMS_SESSION_IDLE_MINUTES_MAX

        duration_deadline = self.obj.session_started_datetime + timedelta(
            minutes=duration_minutes_max
        )
        idle_deadline = self.obj.session_last_activity_datetime + timedelta(
            minutes=idle_minutes_max
        )

        current_datetime = now()

        if current_datetime > duration_deadline:
            return False

        return not current_datetime > idle_deadline

    def session_open(self) -> None:
        current_datetime = now()

        self.obj.session_started_datetime = current_datetime
        self.obj.session_last_activity_datetime = current_datetime
        self.obj.save()

    def session_touch(self) -> None:
        self.obj.session_last_activity_datetime = now()
        self.obj.save()

    def verified_mark(self) -> None:
        self.obj.is_verified = True
        self.obj.verified_datetime = now()
        self.obj.save()
