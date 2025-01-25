from __future__ import annotations

from django_spire.permission.models import PortalUser


def create_user(username: str, password: str) -> PortalUser:
    user = PortalUser.objects.create_user(username=username, password=password)
    user.save()

    return user


def create_super_user() -> PortalUser:
    user = PortalUser.objects.create_user(
        username='bobert@stratusadv.com',
        password='bobert'
    )

    user.is_superuser = True
    user.is_staff = True
    user.first_name = 'Bob'
    user.last_name = 'Robertson'
    user.email = 'bobert@stratusadv.com'

    user.save()

    return user
