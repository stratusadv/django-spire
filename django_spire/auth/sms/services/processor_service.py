from __future__ import annotations

import secrets
from datetime import timedelta
from typing import TYPE_CHECKING

from django.contrib.auth.hashers import check_password, make_password
from django.utils.timezone import now

from django_spire.auth.sms.choices import AuthSmsCodePurposeChoices
from django_spire.auth.sms.constants import CODE_DIGIT_COUNT
from django_spire.conf import settings
from django_spire.contrib.constructor.service import BaseDjangoModelService


if TYPE_CHECKING:
    from django_spire.auth.sms.models import AuthSms


class AuthSmsProcessorService(BaseDjangoModelService['AuthSms']):
    obj: AuthSms

    def clear_code(self) -> None:
        self.obj.services.save_model_obj(
            code_hash='',
            code_purpose='',
            code_expiration_datetime=None,
            code_attempt_count=0,
        )

    def close_session(self) -> None:
        self.obj.services.save_model_obj(
            session_started_datetime=None,
            session_last_activity_datetime=None,
        )

    def confirm_code(self, code: str, purpose: str) -> bool:
        if (
            self.obj.code_hash == ''
            or self.obj.code_purpose != purpose
            or self.obj.code_expiration_datetime is None
        ):
            return False

        if now() > self.obj.code_expiration_datetime:
            self.clear_code()
            return False

        attempt_count_max = settings.DJANGO_SPIRE_AUTH_SMS_CODE_ATTEMPT_COUNT_MAX

        if self.obj.code_attempt_count >= attempt_count_max:
            self.clear_code()
            return False

        if not check_password(code, self.obj.code_hash):
            self.obj.services.save_model_obj(
                code_attempt_count=self.obj.code_attempt_count + 1
            )
            return False

        self.clear_code()

        return True

    def issue_code(self, purpose: str) -> str:
        if purpose not in AuthSmsCodePurposeChoices.values:
            message = f'unknown sms auth purpose: {purpose}'
            raise ValueError(message)

        code = f'{secrets.randbelow(10 ** CODE_DIGIT_COUNT):0{CODE_DIGIT_COUNT}d}'
        expiry_minutes = settings.DJANGO_SPIRE_AUTH_SMS_CODE_EXPIRY_MINUTES

        self.obj.services.save_model_obj(
            code_hash=make_password(code),
            code_purpose=purpose,
            code_expiration_datetime=now() + timedelta(minutes=expiry_minutes),
            code_attempt_count=0,
        )

        return code

    def mark_verified(self) -> None:
        self.obj.services.save_model_obj(is_verified=True, verified_datetime=now())

    def open_session(self) -> None:
        current_datetime = now()

        self.obj.services.save_model_obj(
            session_started_datetime=current_datetime,
            session_last_activity_datetime=current_datetime,
        )

    def touch_session(self) -> None:
        self.obj.services.save_model_obj(session_last_activity_datetime=now())
