from __future__ import annotations

from django.db import models
from django.urls import reverse

from django_spire.contrib.breadcrumb import Breadcrumbs
from django_spire.history.mixins import HistoryModelMixin

from test_project.apps.infinite_scrolling import querysets
from test_project.apps.infinite_scrolling.services.service import InfiniteScrollingService


class InfiniteScrolling(HistoryModelMixin):
    name = models.CharField(max_length=255)
    description = models.TextField(default='')

    objects = querysets.InfiniteScrollingQuerySet().as_manager()
    services = InfiniteScrollingService()

    def __str__(self):
        return self.name

    @classmethod
    def base_breadcrumb(cls) -> Breadcrumbs:
        crumbs = Breadcrumbs()

        crumbs.add_breadcrumb(
            'Infinite Scrolling',
            reverse('infinite_scrolling:page:list')
        )

        return crumbs

    def breadcrumbs(self) -> Breadcrumbs:
        crumbs = Breadcrumbs()
        crumbs.add_base_breadcrumb(self._meta.model)

        if self.pk:
            crumbs.add_breadcrumb(
                str(self),
                reverse(
                    'infinite_scrolling:page:detail',
                    kwargs={'pk': self.pk}
                )
            )

        return crumbs

    class Meta:
        verbose_name = 'Infinite Scrolling'
        verbose_name_plural = 'Infinite Scrollings'
        db_table = 'infinite_scrolling'
