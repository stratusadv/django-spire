from __future__ import annotations

from typing_extensions import TYPE_CHECKING

from django_spire.auth.mfa.models import MfaCode

if TYPE_CHECKING:
    from django.contrib.auth.models import User


def get_or_generate_user_mfa_code(user: User) -> MfaCode:
    mfa_code = MfaCode.objects.valid_code(user)

    if mfa_code:
        return mfa_code

    return MfaCode.generate_code(user)
