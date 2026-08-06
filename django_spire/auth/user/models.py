from __future__ import annotations

from django.contrib.auth.models import User

from django_spire.auth.user import querysets
from django_spire.auth.user.services.services import AuthUserService
from django_spire.history.activity.mixins import ActivityMixin


class AuthUser(User, ActivityMixin):
    objects = querysets.AuthUserManager()
    services = AuthUserService()

    class Meta:
        proxy = True
        verbose_name = 'Auth User'
        verbose_name_plural = 'Auth Users'
