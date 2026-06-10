from __future__ import annotations

from django.db import models
from django.urls import reverse

from django_spire.history.mixins import HistoryModelMixin
from django_spire.history.activity.mixins import ActivityMixin

from django_spire.metric.visual import querysets
from django_spire.metric.visual.services.service import VisualService


class Visual(HistoryModelMixin, ActivityMixin):
    name = models.CharField(max_length=255)
    description = models.TextField(default='')

    objects = querysets.VisualQuerySet().as_manager()
    services = VisualService()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Visual'
        verbose_name_plural = 'Visuals'
        db_table = 'metric_visual'
