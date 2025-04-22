from __future__ import annotations

from django.contrib.auth.models import User
from django.urls import reverse

from django_spire.contrib import Breadcrumbs
from django_spire.history.activity.mixins import ActivityLogMixin


class AuthUser(User, ActivityLogMixin):
    @classmethod
    def base_breadcrumb(cls) -> Breadcrumbs:
        crumbs = Breadcrumbs()
        crumbs.add_breadcrumb('Users', reverse('user_account:list'))
        return crumbs

    def breadcrumbs(self) -> Breadcrumbs:
        crumbs = Breadcrumbs()
        crumbs.add_breadcrumb('User')

        if self.pk:
            crumbs.add_breadcrumb(
                name=self.get_full_name(),
                href=reverse('user_account:detail', kwargs={'pk': self.pk})
            )

        return crumbs

    class Meta:
        proxy = True
        verbose_name = 'User'
        verbose_name_plural = 'Users'
