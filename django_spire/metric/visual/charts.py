from __future__ import annotations

from datetime import date
from typing import Any

from django_spire.contrib.chart.charts import AreaChart, BarChart, GaugeChart, LineChart, PieChart
from django_spire.metric.domain.statistic.constants import (
    StatisticIntervalChoices,
    StatisticValueTypeChoices,
)
from django_spire.metric.visual.choices import VisualKindChoices
from django_spire.metric.visual.models import Visual


def _visual_for(visual_pk: int) -> Visual:
    return Visual.objects.get(pk=visual_pk)


def _value_date(value_date: Any) -> date | None:
    if value_date is None:
        return None

    return date.fromisoformat(value_date) if isinstance(value_date, str) else value_date


def _unit_label(unit_start: date, interval: str, first_year: int) -> str:
    if interval == StatisticIntervalChoices.MONTHLY:
        if unit_start.year == first_year:
            return f'{unit_start:%b}'

        return f'{unit_start:%b} {unit_start.year % 100}'

    return f'{unit_start:%b} {unit_start.day}'


def _unit_x_axis(visual: Visual, value_date: date | None) -> dict:
    datasets = visual.services.transformation.series_datasets(value_date)
    points = datasets[0]['points'] if datasets else []

    labels = []
    if points:
        interval = visual.statistic.interval
        first_year = points[0]['timestamp'].year
        labels = [_unit_label(point['timestamp'], interval, first_year) for point in points]

    return {'type': 'category', 'data': labels, 'axisLabel': {'hideOverlap': True}}


def _series_option(visual: Visual, value_date: date | None) -> list[dict]:
    return [
        {
            'name': dataset['label'],
            'data': [round(float(point['value']), 2) for point in dataset['points']],
        }
        for dataset in visual.services.transformation.series_datasets(value_date)
    ]


class VisualLineChart(LineChart):
    glue_name = 'visual_line_chart'

    @classmethod
    def build_option_body(cls, visual_pk: int, **kwargs: Any) -> dict:
        visual = _visual_for(visual_pk)
        value_date = _value_date(kwargs.get('value_date'))

        return {
            'xAxis': _unit_x_axis(visual, value_date),
            'series': _series_option(visual, value_date),
        }


class VisualBarChart(BarChart):
    glue_name = 'visual_bar_chart'

    @classmethod
    def build_option_body(cls, visual_pk: int, **kwargs: Any) -> dict:
        visual = _visual_for(visual_pk)
        value_date = _value_date(kwargs.get('value_date'))

        return {
            'xAxis': _unit_x_axis(visual, value_date),
            'series': _series_option(visual, value_date),
        }


class VisualAreaChart(AreaChart):
    glue_name = 'visual_area_chart'

    @classmethod
    def build_option_body(cls, visual_pk: int, **kwargs: Any) -> dict:
        visual = _visual_for(visual_pk)
        value_date = _value_date(kwargs.get('value_date'))

        return {
            'xAxis': _unit_x_axis(visual, value_date),
            'series': _series_option(visual, value_date),
        }


class VisualPieChart(PieChart):
    glue_name = 'visual_pie_chart'
    default_legend = {'bottom': 0, 'left': 'center', 'width': '90%'}

    @classmethod
    def build_option_body(cls, visual_pk: int, **kwargs: Any) -> dict:
        visual = _visual_for(visual_pk)
        value_date = _value_date(kwargs.get('value_date'))

        data = visual.services.transformation.series_breakdown(value_date)

        return {
            'series': [
                {
                    'name': visual.name,
                    'label': {'show': True},
                    'center': ['50%', '45%'],
                    'data': data,
                }
            ]
        }


def _gauge_item(dataset: dict, ceiling: int, is_percentage: bool) -> dict:
    value = round(float(dataset['value']), 2)

    if is_percentage:
        return {'value': value, 'name': dataset['label'], 'label': dataset['label']}

    reference = f'{value / ceiling * 100:.1f}%' if ceiling > 0 else ''

    return {'value': value, 'name': reference or dataset['label'], 'label': dataset['label']}


class VisualGaugeChart(GaugeChart):
    glue_name = 'visual_gauge_chart'

    @classmethod
    def build_option_body(cls, visual_pk: int, **kwargs: Any) -> dict:
        visual = _visual_for(visual_pk)
        value_date = _value_date(kwargs.get('value_date'))
        transformation = visual.services.transformation

        statistic = visual.statistic
        is_percentage = (
            statistic is not None and statistic.value_type == StatisticValueTypeChoices.PERCENTAGE
        )
        value_type = statistic.value_type if statistic else StatisticValueTypeChoices.NUMBER

        ceiling = transformation.gauge_max()
        datasets = transformation.dataset_values(value_date)

        return {
            'series': [
                {
                    'name': visual.name,
                    'min': 0,
                    'max': ceiling,
                    'valueType': value_type,
                    'detail': {'offsetCenter': ['0%', '0%']},
                    'title': {'show': not is_percentage, 'offsetCenter': ['0%', '70%']},
                    'data': [_gauge_item(dataset, ceiling, is_percentage) for dataset in datasets],
                }
            ]
        }


VISUAL_CHART_CLASSES: dict[str, type] = {
    VisualKindChoices.LINE: VisualLineChart,
    VisualKindChoices.BAR: VisualBarChart,
    VisualKindChoices.AREA: VisualAreaChart,
    VisualKindChoices.PIE: VisualPieChart,
    VisualKindChoices.GAUGE: VisualGaugeChart,
}
