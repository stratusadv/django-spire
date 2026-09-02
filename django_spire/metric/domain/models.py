from __future__ import annotations

from django.db import models, transaction

from django_spire.history.activity.mixins import ActivityMixin
from django_spire.history.mixins import HistoryModelMixin
from django_spire.history.utils import soft_delete_queryset
from django_spire.metric.domain import querysets
from django_spire.metric.domain.key_utils import unique_key_from_name
from django_spire.metric.domain.services.service import DomainService, SubDomainService
from django_spire.metric.domain.statistic.models import Statistic, StatisticGroup, StatisticValue

__all__ = ['Domain', 'Statistic', 'StatisticGroup', 'StatisticValue', 'SubDomain']


class Domain(HistoryModelMixin, ActivityMixin):
    name = models.CharField(max_length=255)
    description = models.TextField(default='')
    sub_domain_name = models.CharField(max_length=128)

    objects = querysets.DomainQuerySet().as_manager()
    services = DomainService()

    def __str__(self) -> str:
        return self.name

    def set_deleted(self) -> None:
        with transaction.atomic():
            super().set_deleted()

            for subdomain in self.subdomains.all():
                subdomain.set_deleted()

            soft_delete_queryset(self.statistic_groups.all())
            soft_delete_queryset(Statistic.objects.filter(group__domain_id=self.pk))

    class Meta:
        verbose_name = 'Domain'
        verbose_name_plural = 'Domains'
        db_table = 'django_spire_metric_domain'


class SubDomain(HistoryModelMixin, ActivityMixin):
    domain = models.ForeignKey(
        Domain, on_delete=models.CASCADE, related_name='subdomains', related_query_name='subdomain'
    )

    key = models.SlugField(max_length=64, unique=True, blank=True)

    name = models.CharField(max_length=255)
    description = models.TextField(default='')

    objects = querysets.SubDomainQuerySet().as_manager()
    services = SubDomainService()

    def save(self, *args, **kwargs) -> None:
        if self.pk is None and not self.key:
            self.key = unique_key_from_name(self)
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = 'Sub Domain'
        verbose_name_plural = 'Sub Domains'
        db_table = 'django_spire_metric_sub_domain'
