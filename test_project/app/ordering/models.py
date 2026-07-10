from __future__ import annotations

from django.db import models

from django_spire.contrib.constructor.service import BaseDjangoModelService
from django_spire.contrib.ordering.mixins import OrderingModelMixin
from django_spire.history.mixins import HistoryModelMixin

from test_project.app.ordering import querysets


class DuckService(BaseDjangoModelService['Duck']):
    obj: Duck


class Duck(HistoryModelMixin, OrderingModelMixin):
    name = models.CharField(max_length=100)
    color = models.CharField(max_length=7, default='#ff0000')

    objects = querysets.OrderingQuerySet().as_manager()
    services = DuckService()

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = 'Duck'
        verbose_name_plural = 'Ducks'
        db_table = 'apps_ordering'
