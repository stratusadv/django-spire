from __future__ import annotations

from django_spire.permission.models import PortalUser


def create_user(
    username: str,
    password: str,
    **kwargs
) -> PortalUser:
    user, created = PortalUser.objects.get_or_create(
        username=username,
        defaults={
            # 'password': password,
            **kwargs
        }
    )

    # if created:
    #     user.set_password(password)
    #     user.save()

    return user


def create_super_user(password: str = 'bobert', **kwargs) -> PortalUser:
    user, created = PortalUser.objects.get_or_create(
        username='bobert@stratusadv.com',
        defaults={
            'email': 'bobert@stratusadv.com',
            'first_name': 'Bob',
            'last_name': 'Robertson',
            'is_superuser': True,
            'is_staff': True,
            **kwargs
        }
    )

    # if created:
    #     user.set_password(password)
    #     user.save()

    return user
