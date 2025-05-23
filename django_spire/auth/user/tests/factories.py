from __future__ import annotations

from django_spire.auth.user.models import AuthUser


def create_user(
    username: str,
    password: str,
    **kwargs
) -> AuthUser:
    user, created = AuthUser.objects.get_or_create(
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


def create_super_user(password: str = 'stratus', **kwargs) -> AuthUser:
    user, created = AuthUser.objects.get_or_create(
        username='stratus',
        defaults={
            'email': 'bobert@stratusadv.com',
            'first_name': 'Bob',
            'last_name': 'Robertson',
            'is_superuser': True,
            'is_staff': True,
            **kwargs
        }
    )

    if created:
        user.set_password(password)
        user.save()

    return user
