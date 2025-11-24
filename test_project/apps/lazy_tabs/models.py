from __future__ import annotations

from django.db import models
from django.urls import reverse

from django_spire.contrib.breadcrumb import Breadcrumbs
from django_spire.history.activity.mixins import ActivityMixin
from django_spire.history.mixins import HistoryModelMixin

from test_project.apps.lazy_tabs import querysets
from test_project.apps.lazy_tabs.services.service import LazyTabsService


class LazyTabs(ActivityMixin, HistoryModelMixin):
    name = models.CharField(max_length=255)
    description = models.TextField(default='')

    objects = querysets.LazyTabsQuerySet().as_manager()
    services = LazyTabsService()

    def __str__(self):
        return self.name

    @classmethod
    def base_breadcrumb(cls) -> Breadcrumbs:
        crumbs = Breadcrumbs()

        crumbs.add_breadcrumb(
            'Lazy Tabs',
            reverse('lazy_tabs:page:demo')
        )

        return crumbs

    def breadcrumbs(self) -> Breadcrumbs:
        crumbs = Breadcrumbs()
        crumbs.add_base_breadcrumb(self._meta.model)

        if self.pk:
            crumbs.add_breadcrumb(
                str(self),
                reverse(
                    'lazy_tabs:page:demo',
                    kwargs={'pk': self.pk}
                )
            )

        return crumbs

    class Meta:
        verbose_name = 'Lazy Tabs'
        verbose_name_plural = 'Lazy Tabs'
        db_table = 'lazy_tabs'
