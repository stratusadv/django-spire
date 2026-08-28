from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from django_spire.contrib.constructor.service import BaseDjangoModelService
from django_spire.metric.domain.statistic.interval import interval_range
from django_spire.metric.visual.choices import VisualConditionOperatorChoices

if TYPE_CHECKING:
    from datetime import date
    from typing import Any

    from django_spire.metric.visual.models import Visual, VisualCondition


class VisualTransformationService(BaseDjangoModelService['Visual']):
    obj: Visual

    def date_range(self, value_date: date | None = None) -> tuple[date, date]:
        value_date = value_date or self.obj.date

        interval = self.obj.statistic.interval if self.obj.statistic_id else None

        if not interval:
            return value_date, value_date

        return interval_range(interval, value_date)

    def current_value(self, value_date: date | None = None) -> Decimal:
        if not self.obj.statistic_id:
            return Decimal(0)

        start_date, end_date = self.date_range(value_date)

        values = self.obj.statistic.values.date_range(start_date, end_date)

        if self.obj.reference:
            values = values.for_reference(self.obj.reference)

        return values.total()

    def current_condition(
        self, value_date: date | None = None, *, value: Decimal | None = None
    ) -> VisualCondition | None:
        if value is None:
            value = self.current_value(value_date)

        for condition in self.obj.conditions.all():
            if condition.matches(value):
                return condition

        return None

    def series_data(self, value_date: date | None = None) -> list[dict]:
        if not self.obj.statistic_id:
            return []

        start_date, end_date = self.date_range(value_date)

        values = self.obj.statistic.values.date_range(start_date, end_date)

        if self.obj.reference:
            values = values.for_reference(self.obj.reference)

        return [
            {'timestamp': value.timestamp, 'value': value.value}
            for value in values.order_by('timestamp')
        ]

    def series_breakdown(self, value_date: date | None = None) -> list[dict]:
        if not self.obj.statistic_id:
            return []

        start_date, end_date = self.date_range(value_date)

        values = self.obj.statistic.values.date_range(start_date, end_date)

        if self.obj.reference:
            values = values.for_reference(self.obj.reference)

        totals: dict[str, Decimal] = {}

        for value in values:
            reference = value.reference or 'Unassigned'
            totals[reference] = totals.get(reference, Decimal(0)) + value.value

        return [
            {'name': reference, 'value': float(total)}
            for reference, total in sorted(totals.items())
        ]

    def gauge_max(self) -> int:
        ceiling = Decimal(0)

        for condition in self.obj.conditions.all():
            upper = condition.target + condition.tolerance
            ceiling = max(ceiling, upper)

        if ceiling <= 0:
            ceiling = self.current_value() * Decimal(2)

        if ceiling <= 0:
            ceiling = Decimal(100)

        return int(ceiling)

    def chart(self) -> Any | None:
        from django_spire.metric.visual.charts import VISUAL_CHART_CLASSES  # noqa: PLC0415

        chart_class = VISUAL_CHART_CLASSES.get(self.obj.kind)

        if chart_class is None:
            return None

        return chart_class(params={'visual_pk': self.obj.pk})


class VisualConditionTransformationService(BaseDjangoModelService['VisualCondition']):
    obj: VisualCondition

    def matches(self, value: Decimal) -> bool:
        value = Decimal(value)

        comparisons: dict[str, bool] = {
            VisualConditionOperatorChoices.GT: value > self.obj.target,
            VisualConditionOperatorChoices.GTE: value >= self.obj.target,
            VisualConditionOperatorChoices.LT: value < self.obj.target,
            VisualConditionOperatorChoices.LTE: value <= self.obj.target,
            VisualConditionOperatorChoices.EQ: value == self.obj.target,
            VisualConditionOperatorChoices.BETWEEN: abs(value - self.obj.target)
            <= self.obj.tolerance,
        }

        return comparisons.get(self.obj.operator, False)
