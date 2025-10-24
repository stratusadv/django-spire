from __future__ import annotations

from django.db.models import TextChoices


class ListEditorBlockDataStyle(TextChoices):
    UNORDERED = 'unordered'
    ORDERED = 'ordered'
    CHECKLIST = 'checklist'


class OrderedListCounterType(TextChoices):
    NUMERIC = 'numeric'
    UPPER_ROMAN = 'upper-roman'
    LOWER_ROMAN = 'lower-roman'
    UPPER_ALPHA = 'upper-alpha'
    LOWER_ALPHA = 'lower-alpha'
