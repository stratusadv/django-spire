from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Any

from django.utils import timezone

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.metric.domain.statistic.constants import StatisticIntervalChoices
from django_spire.metric.visual.charts import VisualGaugeChart, VisualLineChart
from django_spire.metric.visual.tests.factories import (
    create_test_domain,
    create_test_statistic,
    create_test_statistic_group,
    create_test_subdomain,
    create_test_visual,
)


def aware(value_date: date, hour: int = 12) -> datetime:
    return timezone.make_aware(
        datetime(value_date.year, value_date.month, value_date.day, hour)  # noqa: DTZ001
    )


class VisualChartOptionTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

        domain = create_test_domain()
        self.sub_domain = create_test_subdomain(domain=domain)
        group = create_test_statistic_group(domain=domain)
        self.statistic = create_test_statistic(
            group=group, interval=StatisticIntervalChoices.WEEKLY
        )

    def _chart_option(
        self, kind: str, reference: str = '', references: list[str] | None = None
    ) -> tuple[Any, dict[str, Any]]:
        visual = create_test_visual(
            statistic=self.statistic,
            kind=kind,
            reference=reference,
            references=references,
            with_conditions=False,
        )
        visual.date = date(2026, 5, 15)
        visual.save()

        self.statistic.services.processor.add_value(
            reference='/home/',
            value=Decimal(10),
            sub_domain=self.sub_domain,
            value_timestamp=aware(date(2026, 5, 14), 10),
        )
        self.statistic.services.processor.add_value(
            reference='/home/',
            value=Decimal(20),
            sub_domain=self.sub_domain,
            value_timestamp=aware(date(2026, 5, 15), 11),
        )
        self.statistic.services.processor.add_value(
            reference='/dashboard/',
            value=Decimal(50),
            sub_domain=self.sub_domain,
            value_timestamp=aware(date(2026, 5, 15), 11),
        )
        self.statistic.services.processor.add_value(
            reference='/dashboard/',
            value=Decimal(130),
            sub_domain=self.sub_domain,
            value_timestamp=aware(date(2026, 5, 14), 12),
        )

        chart = visual.services.transformation.chart()
        return chart, chart.to_option_dict()

    def test_line_chart_option(self):
        chart, option = self._chart_option('line', reference='/home/')

        assert chart.glue_name == 'visual_line_chart'
        assert chart.data_function_path.endswith('visual_line_chart_data')
        assert option['xAxis'] == {'type': 'time'}
        assert option['series'][0]['type'] == 'line'

        points = option['series'][0]['data']
        assert len(points) == 2
        assert points[0] == ['2026-05-14', 10.0]
        assert points[1] == ['2026-05-15', 20.0]

    def test_line_chart_option_multiple_datasets(self):
        chart, option = self._chart_option('line', references=['/home/', '/dashboard/'])

        series = option['series']

        assert [item['name'] for item in series] == ['/home/', '/dashboard/']
        assert series[0]['data'] == [['2026-05-14', 10.0], ['2026-05-15', 20.0]]
        assert series[1]['data'] == [['2026-05-14', 130.0], ['2026-05-15', 50.0]]

        assert isinstance(chart, VisualLineChart)

    def test_area_chart_option_has_area_style(self):
        _, option = self._chart_option('area', reference='/home/')

        assert option['series'][0]['type'] == 'line'
        assert 'areaStyle' in option['series'][0]

    def test_pie_chart_option_breaks_down_by_reference(self):
        _, option = self._chart_option('pie')

        slices = option['series'][0]['data']

        assert option['series'][0]['type'] == 'pie'
        assert {'name': '/dashboard/', 'value': 180.0} in slices
        assert {'name': '/home/', 'value': 30.0} in slices

    def test_gauge_chart_option(self):
        visual = create_test_visual(
            statistic=self.statistic,
            kind='gauge',
            target=Decimal(60),
            tolerance=Decimal(0),
            with_conditions=True,
        )
        self.statistic.services.processor.add_value(
            reference='/home/', value=Decimal(50), sub_domain=self.sub_domain
        )

        chart = visual.services.transformation.chart()

        assert isinstance(chart, VisualGaugeChart)
        assert chart.glue_name == 'visual_gauge_chart'

        option = chart.to_option_dict()

        assert option['series'][0]['type'] == 'gauge'
        assert option['series'][0]['min'] == 0
        assert option['series'][0]['max'] == 60
        assert option['series'][0]['data'][0]['value'] == 50.0

    def test_independent_instances_share_one_glue_name(self):
        chart_a, _ = self._chart_option('line', reference='/home/')
        chart_b, _ = self._chart_option('line', reference='/home/')

        assert isinstance(chart_a, VisualLineChart)
        assert isinstance(chart_b, VisualLineChart)
        assert chart_a.glue_name == chart_b.glue_name == 'visual_line_chart'
