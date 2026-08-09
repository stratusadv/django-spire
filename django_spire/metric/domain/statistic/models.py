from __future__ import annotations

from uuid import uuid4

from typing import TYPE_CHECKING

from django.db import models
from django.utils import timezone

from django_spire.history.activity.mixins import ActivityMixin
from django_spire.history.mixins import HistoryModelMixin
from django_spire.metric.domain.statistic import querysets
from django_spire.metric.domain.statistic.constants import StatisticIntervalChoices
from django_spire.metric.domain.statistic.services.service import (
    StatisticGroupService,
    StatisticService,
    StatisticValueService,
)

if TYPE_CHECKING:
    from django.db.models import QuerySet

    from django_spire.metric.domain.models import SubDomain


class StatisticGroup(HistoryModelMixin, ActivityMixin):
    domain = models.ForeignKey(
        'django_spire_metric_domain.Domain',
        on_delete=models.CASCADE,
        related_name='statistic_groups',
        related_query_name='statistic_group',
    )

    name = models.CharField(max_length=255)
    description = models.TextField(default='')

    objects = querysets.StatisticGroupQuerySet().as_manager()
    services = StatisticGroupService()

    class Meta:
        verbose_name = 'Statistic Group'
        verbose_name_plural = 'Statistics Group'
        db_table = 'django_spire_metric_domain_statistic_group'

    def subdomains_qs(self) -> QuerySet[SubDomain]:
        return self.domain.subdomains.active()

    def __str__(self) -> str:
        return self.name


class Statistic(HistoryModelMixin, ActivityMixin):
    key = models.UUIDField(default=uuid4, editable=False, unique=True)

    group = models.ForeignKey(
        StatisticGroup,
        on_delete=models.CASCADE,
        related_name='statistics',
        related_query_name='statistic',
    )

    name = models.CharField(max_length=255)
    interval = models.CharField(
        max_length=20,
        choices=StatisticIntervalChoices.choices,
        default=StatisticIntervalChoices.DAILY,
    )

    objects = querysets.StatisticQuerySet().as_manager()
    services = StatisticService()

    class Meta:
        verbose_name = 'Statistic'
        verbose_name_plural = 'Statistics'
        db_table = 'django_spire_metric_domain_statistic'

    def __str__(self) -> str:
        return self.name


class StatisticValue(models.Model):
    statistic = models.ForeignKey(
        Statistic, on_delete=models.CASCADE, related_name='values', related_query_name='value'
    )

    reference = models.CharField(max_length=255)
    date = models.DateField(default=timezone.localdate)
    value = models.DecimalField(default=0, max_digits=16, decimal_places=4)

    updated_datetime = models.DateTimeField(auto_now=True)

    objects = querysets.StatisticValueQuerySet().as_manager()
    services = StatisticValueService()

    class Meta:
        verbose_name = 'Statistic Value'
        verbose_name_plural = 'Statistic Values'
        db_table = 'django_spire_metric_domain_statistic_value'
        constraints = [
            models.UniqueConstraint(
                fields=('statistic', 'reference', 'date'),
                name='unique_statistic_value_reference_date',
            )
        ]

    def __str__(self) -> str:
        return f'{self.reference} ({self.value})'
