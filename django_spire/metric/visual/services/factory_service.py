from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from django_spire.contrib.constructor.service import BaseDjangoModelService
from django_spire.metric.visual.choices import (
    VisualConditionOperatorChoices,
    VisualConditionStateChoices,
)

if TYPE_CHECKING:
    from django_spire.metric.visual.models import Visual, VisualCondition


class VisualFactoryService(BaseDjangoModelService['Visual']):
    obj: Visual

    def create_default_conditions(
        self, target: Decimal = Decimal(100), tolerance: Decimal = Decimal(10)
    ) -> None:
        self.obj.conditions.all().delete()

        self.obj.conditions.create(
            state=VisualConditionStateChoices.GREEN,
            operator=VisualConditionOperatorChoices.GT,
            target=target,
            order=0,
        )
        self.obj.conditions.create(
            state=VisualConditionStateChoices.YELLOW,
            operator=VisualConditionOperatorChoices.BETWEEN,
            target=target,
            tolerance=tolerance,
            order=1,
        )
        self.obj.conditions.create(
            state=VisualConditionStateChoices.RED,
            operator=VisualConditionOperatorChoices.LT,
            target=target,
            order=2,
        )


class VisualConditionFactoryService(BaseDjangoModelService['VisualCondition']):
    obj: VisualCondition
