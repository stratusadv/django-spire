from __future__ import annotations

from django.db.models import TextChoices


class BlockTypeChoices(TextChoices):
    TEXT = 'text'
    HEADING = 'heading'
    LIST = 'list'
