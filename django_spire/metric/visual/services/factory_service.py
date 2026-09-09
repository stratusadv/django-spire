from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from django_spire.contrib.constructor.service import BaseDjangoModelService
from django_spire.history.activity.context import get_current_user
from django_spire.history.activity.utils import actor_name
from django_spire.metric.visual.choices import (
    VisualConditionOperatorChoices,
    VisualConditionStateChoices,
)

if TYPE_CHECKING:
    from django_spire.metric.visual.models import Visual, VisualCondition, VisualRegion


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


class VisualRegionFactoryService(BaseDjangoModelService['VisualRegion']):
    obj: VisualRegion

    def connect(self, visual: Visual) -> VisualRegion:
        self.obj.visual = visual
        self.obj.save(update_fields=['visual'])

        user = get_current_user()
        if user is not None:
            visual.add_activity(
                user,
                'connected',
                f'{actor_name(user)} connected region "{self.obj}" to "{visual}".',
            )

        return self.obj

    def disconnect(self) -> VisualRegion:
        visual = self.obj.visual
        self.obj.visual = None
        self.obj.save(update_fields=['visual'])

        user = get_current_user()
        if user is not None and visual is not None:
            visual.add_activity(
                user,
                'disconnected',
                f'{actor_name(user)} disconnected region "{self.obj}" from "{visual}".',
            )

        return self.obj
