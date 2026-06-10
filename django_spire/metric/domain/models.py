from __future__ import annotations


from django.db import models
from django.urls import reverse

from django_spire.history.activity.mixins import ActivityMixin
from django_spire.history.mixins import HistoryModelMixin
from django_spire.metric.domain import querysets
from django_spire.metric.domain.services.service import DomainService


class Domain(HistoryModelMixin, ActivityMixin):
    name = models.CharField(max_length=255)
    description = models.TextField(default='')
    sub_domain_description = models.TextField(default='')

    objects = querysets.DomainQuerySet().as_manager()
    services = DomainService()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Domain'
        verbose_name_plural = 'Domains'
        db_table = 'metric_domain'


class SubDomain(HistoryModelMixin, ActivityMixin):
    domain = models.ForeignKey(
        Domain, on_delete=models.CASCADE, related_name='subdomains', related_query_name='subdomain'
    )

    name = models.CharField(max_length=255)
    description = models.TextField(default='')

    objects = querysets.SubDomainQuerySet().as_manager()
    services = DomainService()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Sub_Domain'
        verbose_name_plural = 'Sub Domains'
        db_table = 'metric_sub_domain'
