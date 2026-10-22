from __future__ import annotations

from django.db import models


class CeleryTaskSourceChoices(models.TextChoices):
    USER = ('user', 'User')
    API = ('api', 'API')
    EVENT = ('event', 'Event')
    SCHEDULED = ('scheduled', 'Scheduled')
    SYSTEM = ('system', 'System')
