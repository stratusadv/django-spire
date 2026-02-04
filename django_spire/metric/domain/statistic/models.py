from __future__ import annotations

from decimal import Decimal
from uuid import uuid4

from django.db import models
from django.urls import reverse
from django.utils.timezone import now

from django_spire.contrib.breadcrumb import Breadcrumbs
from django_spire.history.mixins import HistoryModelMixin
from django_spire.history.activity.mixins import ActivityMixin

from django_spire.metric.domain.statistic import querysets
from django_spire.metric.domain.statistic.services.service import StatisticService


class StatisticGroup(HistoryModelMixin, ActivityMixin):
    key = models.UUIDField(default=uuid4, editable=False, unique=True)
    name = models.CharField(max_length=255)
    description = models.TextField(default='')

    objects = querysets.StatisticQuerySet().as_manager()
    services = StatisticService()

    def __str__(self):
        return self.name

    @classmethod
    def base_breadcrumb(cls) -> Breadcrumbs:
        crumbs = Breadcrumbs()

        crumbs.add_breadcrumb(
            'Statistic',
            reverse('metric:domain:statistic:page:list')
        )

        return crumbs

    def breadcrumbs(self) -> Breadcrumbs:
        crumbs = Breadcrumbs()
        crumbs.add_base_breadcrumb(self._meta.model)

        if self.pk:
            crumbs.add_breadcrumb(
                str(self),
                reverse(
                    'metric:domain:statistic:page:detail',
                    kwargs={'pk': self.pk}
                )
            )

        return crumbs

    class Meta:
        verbose_name = 'Statistic Group'
        verbose_name_plural = 'Statistics Group'
        db_table = 'metric_domain_statistic_group'


class Statistic(HistoryModelMixin, ActivityMixin):
    group = models.ForeignKey(
        StatisticGroup,
        on_delete=models.CASCADE,
        related_name='statistics',
        related_query_name='statistic',
        editable=False,
    )
    name = models.CharField(default='', max_length=255, editable=False)
    value = models.DecimalField(default=0, max_digits=16, decimal_places=4, editable=False)
    has_initial_value = models.BooleanField(default=False, editable=False)

    reference_date = models.DateField(default=now, editable=False)

    updated_datetime = models.DateTimeField(default=now, editable=False)
    created_datetime = models.DateTimeField(default=now, editable=False)

    objects = querysets.StatisticQuerySet().as_manager()
    services = StatisticService()

    def __str__(self):
        return self.name

    def add_value(self, value: Decimal):
        self.value += value
        self.has_initial_value = True
        self.save()

    def subtract_value(self, value: Decimal):
        self.value -= value
        self.has_initial_value = True
        self.save()

    def decrement(self):
        self.value -= Decimal(1)
        self.has_initial_value = True
        self.save()

    def increment(self):
        self.value += Decimal(1)
        self.has_initial_value = True
        self.save()

    def set_value(self, value: Decimal):
        self.value = value
        self.has_initial_value = True
        self.save()

    def reset_value(self):
        self.value = 0
        self.has_initial_value = True
        self.save()

    def average_value(self, value: Decimal):
        if self.has_initial_value:
            self.value = Decimal((self.value + value) / 2)
        else:
            self.value = value

        self.has_initial_value = True
        self.save()

    @classmethod
    def base_breadcrumb(cls) -> Breadcrumbs:
        crumbs = Breadcrumbs()

        crumbs.add_breadcrumb(
            'Statistic',
            reverse('metric:domain:statistic:page:list')
        )

        return crumbs

    def breadcrumbs(self) -> Breadcrumbs:
        crumbs = Breadcrumbs()
        crumbs.add_base_breadcrumb(self._meta.model)

        if self.pk:
            crumbs.add_breadcrumb(
                str(self),
                reverse(
                    'metric:domain:statistic:page:detail',
                    kwargs={'pk': self.pk}
                )
            )

        return crumbs

    class Meta:
        verbose_name = 'Statistic'
        verbose_name_plural = 'Statistics'
        db_table = 'metric_domain_statistic'


