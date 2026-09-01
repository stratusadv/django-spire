from __future__ import annotations

from typing import TYPE_CHECKING

from django.db import models, transaction
from django.utils import timezone

from django_spire.history.activity.mixins import ActivityMixin
from django_spire.history.mixins import HistoryModelMixin
from django_spire.history.utils import soft_delete_queryset
from django_spire.metric.domain.key_utils import unique_key_from_name
from django_spire.metric.domain.statistic import querysets
from django_spire.metric.domain.statistic.constants import (
    StatisticIntervalChoices,
    StatisticValueTypeChoices,
)
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
        verbose_name_plural = 'Statistics Groups'
        db_table = 'django_spire_metric_domain_statistic_group'

    # TODO: Move to queryset
    def subdomains_qs(self) -> QuerySet[SubDomain]:
        return self.domain.subdomains.active()

    def set_deleted(self) -> None:
        with transaction.atomic():
            super().set_deleted()
            soft_delete_queryset(self.statistics.all())

    def __str__(self) -> str:
        return self.name


class Statistic(HistoryModelMixin, ActivityMixin):
    key = models.SlugField(max_length=64, unique=True, blank=True)

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
    value_type = models.CharField(
        max_length=20,
        choices=StatisticValueTypeChoices.choices,
        blank=True,
        default=StatisticValueTypeChoices.NUMBER,
    )

    objects = querysets.StatisticQuerySet().as_manager()
    services = StatisticService()

    def save(self, *args, **kwargs) -> None:
        if self.pk is None and not self.key:
            self.key = unique_key_from_name(self)
        super().save(*args, **kwargs)

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

    sub_domain = models.ForeignKey(
        'django_spire_metric_domain.subdomain',
        on_delete=models.CASCADE,
        related_name='values',
        related_query_name='value',
    )

    reference = models.CharField(max_length=255)
    timestamp = models.DateTimeField(default=timezone.now)
    value = models.DecimalField(default=0, max_digits=16, decimal_places=4)

    objects = querysets.StatisticValueQuerySet().as_manager()
    services = StatisticValueService()

    class Meta:
        verbose_name = 'Statistic Value'
        verbose_name_plural = 'Statistic Values'
        db_table = 'django_spire_metric_domain_statistic_value'
        indexes = [
            models.Index(fields=['statistic', 'timestamp'], name='ix_statistic_timestamp'),
            models.Index(
                fields=['statistic', 'sub_domain', 'timestamp'], name='ix_statistic_subdomain_ts'
            ),
            models.Index(
                fields=['statistic', 'reference', 'timestamp'], name='ix_statistic_reference_ts'
            ),
        ]

    def __str__(self) -> str:
        return f'{self.reference} ({self.value})'
