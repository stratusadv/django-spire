from __future__ import annotations

from django.db import models
from django.urls import reverse

from django_spire.history.mixins import HistoryModelMixin
from django_spire.history.activity.mixins import ActivityMixin

from django_spire.metric.visual.signage import querysets
from django_spire.metric.visual.signage.services.service import SignageService


class Signage(HistoryModelMixin, ActivityMixin):
    name = models.CharField(max_length=255)
    description = models.TextField(default='')

    objects = querysets.SignageQuerySet().as_manager()
    services = SignageService()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Signage'
        verbose_name_plural = 'Signages'
        db_table = 'metric_visual_signage'
