from __future__ import annotations

from django.contrib.auth.models import User
from django.urls import reverse

from django_spire.auth.user.services.services import AuthUserService
from django_spire.contrib import Breadcrumbs
from django_spire.history.activity.mixins import ActivityMixin


class AuthUser(User, ActivityMixin):
    services = AuthUserService()

    @classmethod
    def base_breadcrumb(cls) -> Breadcrumbs:
        crumbs = Breadcrumbs()
        crumbs.add_breadcrumb('Users', reverse('django_spire:auth:user:page:list'))
        return crumbs

    def breadcrumbs(self) -> Breadcrumbs:
        crumbs = Breadcrumbs()
        crumbs.add_breadcrumb('User')

        if self.pk:
            crumbs.add_breadcrumb(
                name=self.get_full_name(),
                href=reverse('django_spire:auth:user:page:detail', kwargs={'pk': self.pk})
            )

        return crumbs

    class Meta:
        proxy = True
        verbose_name = 'Auth User'
        verbose_name_plural = 'Auth Users'
