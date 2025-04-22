from __future__ import annotations

from django.contrib.auth.models import Group
from django.urls import reverse

from django_spire.contrib.breadcrumb.breadcrumbs import Breadcrumbs
from django_spire.history.activity.mixins import ActivityLogMixin


class AuthGroup(Group, ActivityLogMixin):
    @classmethod
    def base_breadcrumb(cls) -> Breadcrumbs:
        crumbs = Breadcrumbs()
        crumbs.add_breadcrumb('Groups', reverse('permission:group_list'))
        return crumbs

    def breadcrumbs(self) -> Breadcrumbs:
        crumbs = Breadcrumbs()
        crumbs.add_base_breadcrumb(self._meta.model)

        if self.pk:
            crumbs.add_breadcrumb(
                name=self.name,
                href=reverse(
                    'permission:group_detail',
                    kwargs={'pk': self.pk}
                )
            )

        return crumbs

    class Meta:
        proxy = True
        verbose_name = 'Group'
        verbose_name_plural = 'Groups'


