from __future__ import annotations

from django.db import models
from django_spire.history.mixins import HistoryModelMixin

from test_project.app.history import querysets


class HistoryExample(HistoryModelMixin):
    name = models.CharField(max_length=255)
    description = models.TextField(default='')

    objects = querysets.HistoryExampleQuerySet().as_manager()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'History'
        verbose_name_plural = 'Histories'
        db_table = 'test_project_history'
