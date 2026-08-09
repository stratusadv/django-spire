from __future__ import annotations

from typing import Any

from django_spire.contrib.chart.charts import GaugeChart


class CustomGaugeChart(GaugeChart):
    min = 0
    max = 500

    @classmethod
    def build_option_body(cls, value: float, name: str = '', **kwargs) -> dict[str, Any]:
        return super().build_option_body(value, **{'name': name, **kwargs})


def test_gauge_chart_builds_axis_free_option():
    chart = GaugeChart(params={'value': 75, 'name': 'Score'})

    option = chart.to_option_dict()

    assert 'xAxis' not in option
    assert 'yAxis' not in option
    assert option['series'][0]['type'] == 'gauge'
    assert option['series'][0]['min'] == 0
    assert option['series'][0]['max'] == 100
    assert option['series'][0]['data'][0] == {'value': 75, 'name': 'Score'}


def test_gauge_chart_subclass_overrides_bounds():
    chart = CustomGaugeChart(params={'value': 250, 'name': 'Score'})

    option = chart.to_option_dict()

    assert option['series'][0]['max'] == 500
    assert option['series'][0]['data'][0]['value'] == 250
