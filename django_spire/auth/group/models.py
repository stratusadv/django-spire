from __future__ import annotations

from django.contrib.auth.models import Group
from django.urls import reverse

from django_spire.contrib.breadcrumb.breadcrumbs import Breadcrumbs
from django_spire.history.activity.mixins import ActivityMixin


class AuthGroup(Group, ActivityMixin):
    @classmethod
    def base_breadcrumb(cls) -> Breadcrumbs:
        crumbs = Breadcrumbs()
        crumbs.add_breadcrumb('Groups', reverse('django_spire:auth:group:page:list'))
        return crumbs

    def breadcrumbs(self) -> Breadcrumbs:
        crumbs = Breadcrumbs()
        crumbs.add_base_breadcrumb(self._meta.model)

        if self.pk:
            crumbs.add_breadcrumb(
                name=self.name,
                href=reverse(
                    'django_spire:auth:group:page:detail',
                    kwargs={'pk': self.pk}
                )
            )

        return crumbs

    class Meta:
        proxy = True
        verbose_name = 'Auth Group'
        verbose_name_plural = 'Auth Groups'
