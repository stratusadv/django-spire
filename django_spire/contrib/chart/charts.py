from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Sequence


class Chart:
    chart_type: str = ''

    default_grid = {'left': 40, 'right': 20, 'top': 70, 'bottom': 70}
    default_legend = {'bottom': 5}
    default_tooltip = {'trigger': 'axis'}

    def __init__(
        self,
        title: str | None = None,
        *,
        legend: dict[str, Any] | None = None,
        tooltip: dict[str, Any] | None = None,
        grid: dict[str, Any] | None = None,
    ) -> None:
        self.title = title
        self.categories: list[Any] = []
        self.series: list[dict[str, Any]] = []
        self.legend = {**self.default_legend, **(legend or {})}
        self.tooltip = {**self.default_tooltip, **(tooltip or {})}
        self.grid = {**self.default_grid, **(grid or {})}

    def set_categories(self, categories: Sequence[Any]) -> None:
        self.categories = list(categories)

    def add_series(self, name: str, data: Sequence[Any], **series_options: Any) -> None:
        self.series.append({'name': name, 'data': list(data), **series_options})

    def _series(self) -> list[dict[str, Any]]:
        return [{**series, 'type': self.chart_type} for series in self.series]

    def _option_parts(self) -> dict[str, Any]:
        option = {
            'tooltip': self.tooltip,
            'legend': self.legend,
            'grid': self.grid,
            'series': self._series(),
        }

        if self.title:
            option['title'] = {'text': self.title}

        return option

    def to_option_dict(self) -> dict[str, Any]:
        option = self._option_parts()

        if self.chart_type != 'pie':
            option['xAxis'] = {'type': 'category', 'data': self.categories}
            option['yAxis'] = {'type': 'value'}

        return option


class BarChart(Chart):
    chart_type = 'bar'


class LineChart(Chart):
    chart_type = 'line'


class AreaChart(Chart):
    chart_type = 'line'

    def _series(self) -> list[dict[str, Any]]:
        return [{**series, 'type': 'line', 'areaStyle': {}} for series in self.series]


class PieChart(Chart):
    chart_type = 'pie'
    default_tooltip = {'trigger': 'item'}

    def _series(self) -> list[dict[str, Any]]:
        return [
            {
                **series,
                'type': 'pie',
                'data': [
                    {'name': category, 'value': value}
                    for category, value in zip(self.categories, series['data'], strict=False)
                ],
            }
            for series in self.series
        ]
