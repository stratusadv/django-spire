from __future__ import annotations

from datetime import timedelta
from decimal import Decimal
from typing import TYPE_CHECKING

from django_spire.contrib.constructor.service import BaseDjangoModelService
from django_spire.metric.domain.statistic.constants import (
    StatisticValueTypeChoices,
    percentage_moving_window_days,
)
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

    def _is_percentage(self) -> bool:
        return (
            self.obj.statistic_id
            and self.obj.statistic.value_type == StatisticValueTypeChoices.PERCENTAGE
        )

    def _statistic_values(self) -> Any:
        values = self.obj.statistic.values

        if self.obj.reference:
            values = values.for_reference(self.obj.reference)

        return values

    def current_value(self, value_date: date | None = None) -> Decimal:
        if not self.obj.statistic_id:
            return Decimal(0)

        value_date = value_date or self.obj.date
        values = self._statistic_values()

        if self._is_percentage():
            window_days = percentage_moving_window_days(self.obj.statistic.interval)
            return values.moving_window_average(value_date, window_days)

        start_date, end_date = self.date_range(value_date)
        return values.date_range(start_date, end_date).total()

    def current_condition(
        self, value_date: date | None = None, *, value: Decimal | None = None
    ) -> VisualCondition | None:
        if value is None:
            value = self.current_value(value_date)

        for condition in self.obj.conditions.all():
            if condition.matches(value):
                return condition

        return None

    def _percentage_series(self, value_date: date, window_days: int) -> list[dict]:
        start_date = value_date - timedelta(days=window_days - 1)
        fetch_start = start_date - timedelta(days=window_days - 1)

        daily_averages = dict(
            self._statistic_values().daily_averages(fetch_start, value_date)
        )

        points = []
        for day_offset in range(window_days):
            day = start_date + timedelta(days=day_offset)

            window_total = Decimal(0)
            window_count = 0
            for back in range(window_days):
                d = day - timedelta(days=back)
                if d in daily_averages:
                    window_total += daily_averages[d]
                    window_count += 1

            if window_count == 0:
                continue

            points.append({'timestamp': day, 'value': float(window_total / window_count)})

        return points

    def series_data(self, value_date: date | None = None) -> list[dict]:
        if not self.obj.statistic_id:
            return []

        value_date = value_date or self.obj.date

        if self._is_percentage():
            window_days = percentage_moving_window_days(self.obj.statistic.interval)
            return self._percentage_series(value_date, window_days)

        start_date, end_date = self.date_range(value_date)

        values = self._statistic_values().date_range(start_date, end_date)

        return [
            {'timestamp': value.timestamp, 'value': value.value}
            for value in values.order_by('timestamp')
        ]

    def series_breakdown(self, value_date: date | None = None) -> list[dict]:
        if not self.obj.statistic_id:
            return []

        start_date, end_date = self.date_range(value_date)

        values = self._statistic_values().date_range(start_date, end_date)

        if self._is_percentage():
            sums: dict[str, Decimal] = {}
            counts: dict[str, int] = {}

            for value in values:
                reference = value.reference or 'Unassigned'
                sums[reference] = sums.get(reference, Decimal(0)) + value.value
                counts[reference] = counts.get(reference, 0) + 1

            return [
                {'name': reference, 'value': float(sums[reference] / counts[reference])}
                for reference in sorted(sums)
            ]

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
