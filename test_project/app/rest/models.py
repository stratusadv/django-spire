from __future__ import annotations

from django.db import models

from django_spire.history.activity.mixins import ActivityMixin
from django_spire.history.mixins import HistoryModelMixin


class Pirate(ActivityMixin, HistoryModelMixin):
    """Test model for demonstrating REST client/service integration."""
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.EmailField()
    username = models.CharField(max_length=150, unique=True)

    class Meta:
        verbose_name = "Pirate"
        verbose_name_plural = "Pirates"

    def __str__(self):
        return self.username
