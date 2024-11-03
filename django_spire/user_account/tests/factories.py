from __future__ import annotations

from django_spire.permission.models import PortalUser


def create_user(username: str, password: str) -> PortalUser:
    user = PortalUser.objects.create_user(username=username, password=password)
    user.save()
    return user


def create_super_user() -> PortalUser:
    user = PortalUser.objects.create_user(
        username='Super Goat',
        password='goatty_99'
    )
    user.is_superuser = True
    user.is_staff = True
    user.save()
    return user
