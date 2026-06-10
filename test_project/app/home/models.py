from __future__ import annotations

from django.db import models
from django_spire.history.mixins import HistoryModelMixin

from test_project.app.home import querysets


class HomeExample(HistoryModelMixin):
    name = models.CharField(max_length=255)
    description = models.TextField(default='')

    objects = querysets.HomeExampleQuerySet().as_manager()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Home'
        verbose_name_plural = 'Homes'
        db_table = 'test_project_home'
