from __future__ import annotations

from django_spire.auth.user.models import AuthUser


def register_new_user(
    first_name: str,
    last_name: str,
    email: str,
    password: str
) -> AuthUser:
    return AuthUser.objects.create_user(
        username=email.lower(),
        email=email.lower(),
        password=password,
        first_name=first_name,
        last_name=last_name
    )
