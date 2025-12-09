from __future__ import annotations

from django.db import models


class HistoryEventChoices(models.TextChoices):
    CREATED = 'crea', 'Created'
    UPDATED = 'upda', 'Updated'
    ACTIVE = 'acti', 'Active'
    INACTIVE = 'inac', 'Inactive'
    DELETED = 'dele', 'Deleted'
    UNDELETED = 'unde', 'Un-Deleted'
