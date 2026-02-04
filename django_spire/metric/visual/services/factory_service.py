from __future__ import annotations

from typing import TYPE_CHECKING

from django_spire.contrib.service import BaseDjangoModelService

if TYPE_CHECKING:
    from django_spire.metric.visual.models import Visual


class VisualFactoryService(BaseDjangoModelService['Visual']):
    obj: Visual
