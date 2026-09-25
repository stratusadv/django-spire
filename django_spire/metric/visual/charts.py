from __future__ import annotations

from datetime import date
from typing import Any

from django_spire.contrib.chart.charts import AreaChart, BarChart, GaugeChart, LineChart, PieChart
from django_spire.metric.visual.choices import VisualKindChoices
from django_spire.metric.visual.models import Visual


def _visual_for(visual_pk: int) -> Visual:
    return Visual.objects.get(pk=visual_pk)


def _value_date(value_date: Any) -> date | None:
    if value_date is None:
        return None

    return date.fromisoformat(value_date) if isinstance(value_date, str) else value_date


def _series_option(visual: Visual, value_date: date | None) -> list[dict]:
    return [
        {
            'name': dataset['label'],
            'data': [
                [point['timestamp'].isoformat(), round(float(point['value']), 2)]
                for point in dataset['points']
            ],
        }
        for dataset in visual.services.transformation.series_datasets(value_date)
    ]


class VisualLineChart(LineChart):
    glue_name = 'visual_line_chart'

    @classmethod
    def build_option_body(cls, visual_pk: int, **kwargs: Any) -> dict:
        visual = _visual_for(visual_pk)
        value_date = _value_date(kwargs.get('value_date'))

        return {'xAxis': {'type': 'time'}, 'series': _series_option(visual, value_date)}


class VisualBarChart(BarChart):
    glue_name = 'visual_bar_chart'

    @classmethod
    def build_option_body(cls, visual_pk: int, **kwargs: Any) -> dict:
        visual = _visual_for(visual_pk)
        value_date = _value_date(kwargs.get('value_date'))

        return {'xAxis': {'type': 'time'}, 'series': _series_option(visual, value_date)}


class VisualAreaChart(AreaChart):
    glue_name = 'visual_area_chart'

    @classmethod
    def build_option_body(cls, visual_pk: int, **kwargs: Any) -> dict:
        visual = _visual_for(visual_pk)
        value_date = _value_date(kwargs.get('value_date'))

        return {'xAxis': {'type': 'time'}, 'series': _series_option(visual, value_date)}


class VisualPieChart(PieChart):
    glue_name = 'visual_pie_chart'

    @classmethod
    def build_option_body(cls, visual_pk: int, **kwargs: Any) -> dict:
        visual = _visual_for(visual_pk)
        value_date = _value_date(kwargs.get('value_date'))

        data = visual.services.transformation.series_breakdown(value_date)

        return {'series': [{'name': visual.name, 'data': data}]}


class VisualGaugeChart(GaugeChart):
    glue_name = 'visual_gauge_chart'

    @classmethod
    def build_option_body(cls, visual_pk: int, **kwargs: Any) -> dict:
        visual = _visual_for(visual_pk)
        value_date = _value_date(kwargs.get('value_date'))

        ceiling = visual.services.transformation.gauge_max()
        datasets = visual.services.transformation.dataset_values(value_date)

        return {
            'series': [
                {
                    'name': visual.name,
                    'min': 0,
                    'max': ceiling,
                    'detail': {'formatter': '{value}'},
                    'data': [
                        {'value': round(float(dataset['value']), 2), 'name': dataset['label']}
                        for dataset in datasets
                    ],
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
