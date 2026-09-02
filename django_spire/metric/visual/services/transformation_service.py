from __future__ import annotations

from datetime import timedelta
from decimal import Decimal
from typing import TYPE_CHECKING

from django.core.cache import cache
from django.db.models import Max

from django_spire.contrib.constructor.service import BaseDjangoModelService
from django_spire.metric.domain.statistic.constants import (
    StatisticValueTypeChoices,
    percentage_moving_window_days,
)
from django_spire.metric.domain.statistic.interval import interval_range
from django_spire.metric.domain.statistic.querysets import reference_matches
from django_spire.metric.visual.choices import VisualConditionOperatorChoices

if TYPE_CHECKING:
    from datetime import date
    from typing import Any

    from django_spire.metric.visual.models import (
        Visual,
        VisualCondition,
        VisualReference,
        VisualRegion,
    )


VISUAL_AGGREGATE_CACHE_TTL_SECONDS = 120


class VisualTransformationService(BaseDjangoModelService['Visual']):
    obj: Visual

    def _value_revision(self) -> str:
        if not self.obj.statistic_id:
            return 'none'

        latest = self.obj.statistic.values.aggregate(latest=Max('timestamp'))['latest']
        return str(latest).replace(':', '-').replace(' ', '_') if latest is not None else 'none'

    def _cache_key(
        self,
        kind: str,
        *,
        value_date: date | None = None,
        reference: str | None = None,
        include_conditions: bool = False,
    ) -> str:
        value_date = value_date or self.obj.date

        parts = [
            'metric:visual',
            self.obj.pk,
            self.obj.statistic_id or 'none',
            kind,
            value_date.isoformat(),
            self._value_revision(),
            reference or '-',
        ]
        if reference is None:
            datasets = self._datasets()
            parts.append('|'.join(f'{d.reference}->{d}' for d in datasets) if datasets else '-')
        if include_conditions:
            parts.append(
                '|'.join(
                    f'{condition.target}-{condition.tolerance}'
                    for condition in self.obj.conditions.all()
                )
            )

        return ':'.join(str(part) for part in parts)

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

    def _statistic_deleted(self) -> bool:
        return bool(self.obj.statistic_id and self.obj.statistic.is_deleted)

    def _datasets(self) -> list[VisualReference]:
        return list(self.obj.references.all())

    def _values_for(self, reference: str) -> Any:
        return self.obj.statistic.values.for_reference_pattern(reference)

    def _all_values(self) -> Any:
        patterns = [ref.reference for ref in self._datasets()]

        return self.obj.statistic.values.for_reference_patterns(patterns)

    def _statistic_values(self) -> Any:
        datasets = self._datasets()

        if not datasets:
            return self.obj.statistic.values

        return self._values_for(datasets[0].reference)

    def current_value(
        self, value_date: date | None = None, *, reference: str | None = None
    ) -> Decimal:
        if not self.obj.statistic_id:
            return Decimal(0)

        if self._statistic_deleted():
            return Decimal(0)

        key = self._cache_key('value', value_date=value_date, reference=reference)
        cached = cache.get(key)
        if cached is not None:
            return cached

        value_date = value_date or self.obj.date

        values = self._values_for(reference) if reference is not None else self._statistic_values()

        if self._is_percentage():
            window_days = percentage_moving_window_days(self.obj.statistic.interval)
            result = values.moving_window_average(value_date, window_days)
        else:
            start_date, end_date = self.date_range(value_date)
            result = values.date_range(start_date, end_date).total()

        cache.set(key, result, VISUAL_AGGREGATE_CACHE_TTL_SECONDS)
        return result

    def current_condition(
        self, value_date: date | None = None, *, value: Decimal | None = None
    ) -> VisualCondition | None:
        if value is None:
            value = self.current_value(value_date)

        for condition in self.obj.conditions.all():
            if condition.matches(value):
                return condition

        return None

    def _percentage_series(self, value_date: date, window_days: int, values: Any) -> list[dict]:
        start_date = value_date - timedelta(days=window_days - 1)
        fetch_start = start_date - timedelta(days=window_days - 1)

        daily_averages = dict(values.daily_averages(fetch_start, value_date))

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

    def _series_points(self, value_date: date, values: Any) -> list[dict]:
        if self._is_percentage():
            window_days = percentage_moving_window_days(self.obj.statistic.interval)
            return self._percentage_series(value_date, window_days, values)

        start_date, end_date = self.date_range(value_date)

        return [
            {'timestamp': day, 'value': float(total)}
            for day, total in values.series_points(start_date, end_date)
        ]

    def series_datasets(self, value_date: date | None = None) -> list[dict]:
        if not self.obj.statistic_id:
            return []

        if self._statistic_deleted():
            return []

        key = self._cache_key('series', value_date=value_date)
        cached = cache.get(key)
        if cached is not None:
            return cached

        value_date = value_date or self.obj.date

        datasets = self._datasets()

        if not datasets:
            result = [
                {
                    'label': self.obj.name,
                    'points': self._series_points(value_date, self._statistic_values()),
                }
            ]
        else:
            result = [
                {
                    'label': str(dataset),
                    'points': self._series_points(value_date, self._values_for(dataset.reference)),
                }
                for dataset in datasets
            ]

        cache.set(key, result, VISUAL_AGGREGATE_CACHE_TTL_SECONDS)
        return result

    def series_data(self, value_date: date | None = None) -> list[dict]:
        datasets = self.series_datasets(value_date)

        if not datasets:
            return []

        return datasets[0]['points']

    def series_breakdown(self, value_date: date | None = None) -> list[dict]:
        if not self.obj.statistic_id:
            return []

        if self._statistic_deleted():
            return []

        key = self._cache_key('breakdown', value_date=value_date)
        cached = cache.get(key)
        if cached is not None:
            return cached

        start_date, end_date = self.date_range(value_date)

        values = self._all_values()

        if self._is_percentage():
            breakdown = values.breakdown(start_date, end_date, average=True)
        else:
            breakdown = values.breakdown(start_date, end_date)

        labels = {dataset.reference: str(dataset) for dataset in self._datasets()}

        result = [
            {
                'name': next(
                    (label for pattern, label in labels.items() if reference_matches(pattern, ref)),
                    ref,
                ),
                'value': float(total),
            }
            for ref, total in breakdown
        ]
        cache.set(key, result, VISUAL_AGGREGATE_CACHE_TTL_SECONDS)
        return result

    def dataset_values(self, value_date: date | None = None) -> list[dict]:
        if not self.obj.statistic_id:
            return []

        if self._statistic_deleted():
            return []

        key = self._cache_key('dataset-values', value_date=value_date)
        cached = cache.get(key)
        if cached is not None:
            return cached

        value_date = value_date or self.obj.date

        datasets = self._datasets()

        if not datasets:
            result = [{'label': self.obj.name, 'value': self.current_value(value_date)}]
        else:
            result = [
                {
                    'label': str(dataset),
                    'value': self.current_value(value_date, reference=dataset.reference),
                }
                for dataset in datasets
            ]

        cache.set(key, result, VISUAL_AGGREGATE_CACHE_TTL_SECONDS)
        return result

    def gauge_max(self) -> int:
        key = self._cache_key('gauge', include_conditions=True)
        cached = cache.get(key)
        if cached is not None:
            return cached

        ceiling = Decimal(0)

        for condition in self.obj.conditions.all():
            upper = condition.target + condition.tolerance
            ceiling = max(ceiling, upper)

        if ceiling <= 0:
            ceiling = self.current_value() * Decimal(2)

        if ceiling <= 0:
            ceiling = Decimal(100)

        result = int(ceiling)
        cache.set(key, result, VISUAL_AGGREGATE_CACHE_TTL_SECONDS)
        return result

    def chart(self) -> Any | None:
        from django_spire.metric.visual.charts import VISUAL_CHART_CLASSES  # noqa: PLC0415

        chart_class = VISUAL_CHART_CLASSES.get(self.obj.kind)

        if chart_class is None:
            return None

        return chart_class(params={'visual_pk': self.obj.pk})

    def render_context(self) -> dict:
        if self.obj.is_deleted or self._statistic_deleted():
            return self.empty_render_context()

        current_value = self.current_value()
        period_start, period_end = self.date_range()

        return {
            'visual': self.obj,
            'current_value': current_value,
            'current_condition': self.current_condition(value=current_value),
            'chart': self.chart(),
            'period_start': period_start,
            'period_end': period_end,
        }

    @staticmethod
    def empty_render_context() -> dict:
        return {'visual': None, 'current_value': None, 'current_condition': None, 'chart': None}


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


class VisualRegionTransformationService(BaseDjangoModelService['VisualRegion']):
    obj: VisualRegion

    @property
    def display_title(self) -> str:
        if self.obj.title:
            return self.obj.title

        if self.obj.visual_id:
            return self.obj.visual.name

        return self.obj.key

    def render_context(self) -> dict:
        if not self.obj.visual_id or self.obj.visual.is_deleted:
            context = VisualTransformationService.empty_render_context()
        else:
            context = self.obj.visual.services.transformation.render_context()

        context['display_title'] = self.display_title
        return context
