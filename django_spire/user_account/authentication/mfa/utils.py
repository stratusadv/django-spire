from django.contrib.auth.models import User

from django_spire.user_account.authentication.mfa.models import MfaCode


def get_or_generate_user_mfa_code(user: User) -> MfaCode:
    mfa_code = MfaCode.objects.valid_code(user)

    if mfa_code:
        return mfa_code
    else:
        return MfaCode.generate_code(user)