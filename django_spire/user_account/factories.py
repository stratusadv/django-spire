from __future__ import annotations

from typing_extensions import TYPE_CHECKING

from django_spire.permission.models import PortalUser
from django_spire.user_account.profile.models import UserProfile

if TYPE_CHECKING:
    from django.contrib.auth.models import User


def get_or_create_user_profile(user: User) -> UserProfile:
    try:
        return user.profile
    except UserProfile.DoesNotExist:
        return create_user_profile(user)


def create_user_profile(user: User) -> UserProfile:
    return UserProfile.objects.create(user=user)


def register_new_user(
        first_name: str,
        last_name: str,
        email: str,
        password: str
) -> PortalUser:
    return PortalUser.objects.create_user(
        username=email.lower(),
        email=email.lower(),
        password=password,
        first_name=first_name,
        last_name=last_name
    )
