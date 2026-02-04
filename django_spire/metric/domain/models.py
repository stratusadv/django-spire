from __future__ import annotations

from django.db import models
from django.urls import reverse

from django_spire.contrib.breadcrumb import Breadcrumbs
from django_spire.history.mixins import HistoryModelMixin
from django_spire.history.activity.mixins import ActivityMixin

from django_spire.metric.domain import querysets
from django_spire.metric.domain.services.service import DomainService


class Domain(HistoryModelMixin, ActivityMixin):
    name = models.CharField(max_length=255)
    description = models.TextField(default='')

    objects = querysets.DomainQuerySet().as_manager()
    services = DomainService()

    def __str__(self):
        return self.name

    @classmethod
    def base_breadcrumb(cls) -> Breadcrumbs:
        crumbs = Breadcrumbs()

        crumbs.add_breadcrumb(
            'Domain',
            reverse('metric:domain:page:list')
        )

        return crumbs

    def breadcrumbs(self) -> Breadcrumbs:
        crumbs = Breadcrumbs()
        crumbs.add_base_breadcrumb(self._meta.model)

        if self.pk:
            crumbs.add_breadcrumb(
                str(self),
                reverse(
                    'metric:domain:page:detail',
                    kwargs={'pk': self.pk}
                )
            )

        return crumbs

    class Meta:
        verbose_name = 'Domain'
        verbose_name_plural = 'Domains'
        db_table = 'metric_domain'
