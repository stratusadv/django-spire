from __future__ import annotations

from django.db import models
from django.urls import reverse

from django_spire.history.mixins import HistoryModelMixin
from django_spire.history.activity.mixins import ActivityMixin

from django_spire.metric.visual.presentation import querysets
from django_spire.metric.visual.presentation.services.service import PresentationService


class Presentation(HistoryModelMixin, ActivityMixin):
    name = models.CharField(max_length=255)
    description = models.TextField(default='')

    objects = querysets.PresentationQuerySet().as_manager()
    services = PresentationService()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Presentation'
        verbose_name_plural = 'Presentations'
        db_table = 'metric_visual_presentation'
