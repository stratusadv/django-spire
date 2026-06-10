from __future__ import annotations

from django.contrib.auth.models import Group
from django.urls import reverse

from django_spire.contrib.navigation.breadcrumbs import Breadcrumbs
from django_spire.history.activity.mixins import ActivityMixin


class AuthGroup(Group, ActivityMixin):
    class Meta:
        proxy = True
        verbose_name = 'Auth Group'
        verbose_name_plural = 'Auth Groups'
