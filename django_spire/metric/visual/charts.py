from __future__ import annotations

from typing import TYPE_CHECKING

from django_spire.contrib.chart.charts import AreaChart, BarChart, GaugeChart, LineChart, PieChart
from django_spire.metric.visual.choices import VisualKindChoices
from django_spire.metric.visual.models import Visual

if TYPE_CHECKING:
    from typing import Any


def _visual_for(visual_pk: int) -> Visual:
    return Visual.objects.get(pk=visual_pk)


class VisualLineChart(LineChart):
    glue_name = 'visual_line_chart'

    @classmethod
    def build_option_body(cls, visual_pk: int, **_kwargs: Any) -> dict:
        visual = _visual_for(visual_pk)

        points = visual.services.transformation.series_data()

        return {
            'xAxis': {'type': 'time'},
            'series': [
                {
                    'name': visual.name,
                    'data': [
                        [point['timestamp'].isoformat(), float(point['value'])] for point in points
                    ],
                }
            ],
        }


class VisualBarChart(BarChart):
    glue_name = 'visual_bar_chart'

    @classmethod
    def build_option_body(cls, visual_pk: int, **_kwargs: Any) -> dict:
        visual = _visual_for(visual_pk)

        points = visual.services.transformation.series_data()

        return {
            'xAxis': {'type': 'time'},
            'series': [
                {
                    'name': visual.name,
                    'data': [
                        [point['timestamp'].isoformat(), float(point['value'])] for point in points
                    ],
                }
            ],
        }


class VisualAreaChart(AreaChart):
    glue_name = 'visual_area_chart'

    @classmethod
    def build_option_body(cls, visual_pk: int, **_kwargs: Any) -> dict:
        visual = _visual_for(visual_pk)

        points = visual.services.transformation.series_data()

        return {
            'xAxis': {'type': 'time'},
            'series': [
                {
                    'name': visual.name,
                    'data': [
                        [point['timestamp'].isoformat(), float(point['value'])] for point in points
                    ],
                }
            ],
        }


class VisualPieChart(PieChart):
    glue_name = 'visual_pie_chart'

    @classmethod
    def build_option_body(cls, visual_pk: int, **_kwargs: Any) -> dict:
        visual = _visual_for(visual_pk)

        data = visual.services.transformation.series_breakdown()

        return {'series': [{'name': visual.name, 'data': data}]}


class VisualGaugeChart(GaugeChart):
    glue_name = 'visual_gauge_chart'

    @classmethod
    def build_option_body(cls, visual_pk: int, **_kwargs: Any) -> dict:
        visual = _visual_for(visual_pk)

        value = float(visual.services.transformation.current_value())
        ceiling = visual.services.transformation.gauge_max()

        return {
            'series': [
                {
                    'name': visual.name,
                    'min': 0,
                    'max': ceiling,
                    'detail': {'formatter': '{value}'},
                    'data': [{'value': value, 'name': visual.name}],
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
