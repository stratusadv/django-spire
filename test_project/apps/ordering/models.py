from __future__ import annotations

from django.db import models
from django.urls import reverse

from django_spire.contrib.breadcrumb import Breadcrumbs
from django_spire.contrib.ordering.mixins import OrderingModelMixin
from django_spire.history.mixins import HistoryModelMixin

from test_project.apps.ordering import querysets
from test_project.apps.ordering.services.service import OrderingService


class Duck(HistoryModelMixin, OrderingModelMixin):
    name = models.CharField(max_length=100)

    color = models.CharField(
        max_length=7,
        default='#ff0000',
    )

    objects = querysets.OrderingQuerySet().as_manager()
    services = OrderingService()

    def __str__(self):
        return self.name

    @classmethod
    def base_breadcrumb(cls) -> Breadcrumbs:
        crumbs = Breadcrumbs()

        crumbs.add_breadcrumb(
            'Ordering',
            reverse('apps:ordering:page:list')
        )

        return crumbs

    def breadcrumbs(self) -> Breadcrumbs:
        crumbs = Breadcrumbs()
        crumbs.add_base_breadcrumb(self._meta.model)

        if self.pk:
            crumbs.add_breadcrumb(
                str(self),
                reverse(
                    'apps:ordering:page:detail',
                    kwargs={'pk': self.pk}
                )
            )

        return crumbs

    class Meta:
        verbose_name = 'Ordering'
        verbose_name_plural = 'Orderings'
        db_table = 'apps_ordering'