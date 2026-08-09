from __future__ import annotations

from typing import TYPE_CHECKING

from django_spire.contrib.constructor.service import BaseDjangoModelService

if TYPE_CHECKING:
    from django_spire.metric.visual.models import Visual, VisualCondition


class VisualProcessorService(BaseDjangoModelService['Visual']):
    obj: Visual


class VisualConditionProcessorService(BaseDjangoModelService['VisualCondition']):
    obj: VisualCondition
