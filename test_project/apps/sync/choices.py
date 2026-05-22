from __future__ import annotations

from django.db.models import TextChoices


class SiteStatusChoices(TextChoices):
    PLANNING = 'planning', 'Planning'
    ACTIVE = 'active', 'Active'
    COMPLETE = 'complete', 'Complete'


class PlanStatusChoices(TextChoices):
    DRAFT = 'draft', 'Draft'
    IN_PROGRESS = 'in-progress', 'In Progress'
    REVIEWED = 'reviewed', 'Reviewed'


class LineDirectionChoices(TextChoices):
    NS = 'NS', 'North-South'
    EW = 'EW', 'East-West'
    NE_SW = 'NE-SW', 'Northeast-Southwest'
    NW_SE = 'NW-SE', 'Northwest-Southeast'


class StakeTypeChoices(TextChoices):
    BOUNDARY = 'boundary', 'Boundary'
    CONTROL = 'control', 'Control'
    OFFSET = 'offset', 'Offset'
    REFERENCE = 'reference', 'Reference'
