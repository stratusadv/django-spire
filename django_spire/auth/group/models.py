from __future__ import annotations

from django.contrib.auth.models import Group

from django_spire.auth.group.services.services import AuthGroupService
from django_spire.history.activity.mixins import ActivityMixin
from django_spire.auth.group import querysets

class AuthGroup(Group, ActivityMixin):
    # objects = querysets.AuthGroupManager()
    service = AuthGroupService()

    class Meta:
        proxy = True
        verbose_name = 'Auth Group'
        verbose_name_plural = 'Auth Groups'
