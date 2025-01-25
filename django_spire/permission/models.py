from __future__ import annotations

from django.contrib.auth.models import Group, User
from django.urls import reverse

from django_spire.breadcrumb.models import Breadcrumbs
from django_spire.history.mixins import ActivityLogMixin


class PortalGroup(Group, ActivityLogMixin):
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


class PortalUser(User, ActivityLogMixin):
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
