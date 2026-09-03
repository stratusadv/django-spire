from __future__ import annotations

from django.utils import timezone

from django_spire.auth.user.models import AuthUser


def create_user(username: str, **kwargs) -> AuthUser:
    user, _ = AuthUser.objects.get_or_create(username=username, defaults={**kwargs})

    return user


def create_super_user(password: str = 'stratus', **kwargs) -> AuthUser:
    defaults = {
        'email': 'bobert@stratusadv.com',
        'first_name': 'Bob',
        'last_name': 'Robertson',
        'is_superuser': True,
        'is_staff': True,
        'last_login': timezone.now(),
        **kwargs,
    }

    user, _ = AuthUser.objects.update_or_create(username='stratus', defaults=defaults)

    user.set_password(password)
    user.save()

    return user

def get_default_super_user() -> AuthUser:
    super_user = AuthUser.objects.filter(username='stratus', email='bobert@stratusadv.com', is_superuser=True).first()

    if super_user is None:
        super_user = create_super_user()

    return super_user