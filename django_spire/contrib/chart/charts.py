from __future__ import annotations

import re
import sys
from typing import TYPE_CHECKING, Any

from django_glue import Glue

if TYPE_CHECKING:
    from django.http import HttpRequest


def _snake_case(name: str) -> str:
    return re.sub(r'(?<!^)(?=[A-Z])', '_', name).lower()


class Chart:
    chart_type: str = ''

    default_grid: dict[str, Any] = {'left': 50, 'right': 20, 'top': 20, 'bottom': 80}
    default_legend: dict[str, Any] = {'bottom': 30}
    default_tooltip: dict[str, Any] = {'trigger': 'axis'}

    title: str | None = None
    legend: dict[str, Any] = {}
    tooltip: dict[str, Any] = {}
    grid: dict[str, Any] = {}

    params: dict[str, Any] = {}

    glue_name: str | None = None
    data_function_path: str | None = None
    update_interval: float = 3

    def __init__(self, params: dict[str, Any] | None = None) -> None:
        self.params = {**type(self).params, **(params or {})}

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)

        option_owner = next(
            (base for base in cls.__mro__ if 'build_option_body' in base.__dict__), None
        )

        if option_owner is None or option_owner is Chart:
            return

        cls.glue_name = cls.__dict__.get('glue_name', _snake_case(cls.__name__))

        data_attr = f'{_snake_case(cls.__name__)}_data'
        setattr(sys.modules[cls.__module__], data_attr, cls._build_option)
        cls.data_function_path = f'{cls.__module__}.{data_attr}'

    @classmethod
    def build_option_body(cls, **kwargs: Any) -> dict[str, Any]:
        message = f'{cls.__name__} must implement build_option_body(**kwargs)'
        raise NotImplementedError(message)

    @classmethod
    def _build_option(cls, **kwargs: Any) -> dict[str, Any]:
        option: dict[str, Any] = {
            'legend': {**cls.default_legend, **cls.legend},
            'tooltip': {**cls.default_tooltip, **cls.tooltip},
            'grid': {**cls.default_grid, **cls.grid},
        }

        if cls.title:
            option['title'] = {'text': cls.title}

        if cls.chart_type not in ('pie', 'gauge'):
            option['xAxis'] = {'type': 'category', 'data': []}
            option['yAxis'] = {'type': 'value'}

        data = cls.build_option_body(**kwargs)
        series = [
            {**item, 'type': item.get('type', cls.chart_type)} for item in data.get('series', [])
        ]

        return {**option, **data, 'series': series}

    def to_option_dict(self, **kwargs: Any) -> dict[str, Any]:
        return type(self)._build_option(**{**self.params, **kwargs})

    def glue(self, request: HttpRequest) -> None:
        if not self.data_function_path:
            message = f'{type(self).__name__} has no data_function_path to glue'
            raise ValueError(message)

        Glue.function(request, self.glue_name, self.data_function_path)


class BarChart(Chart):
    chart_type = 'bar'


class LineChart(Chart):
    chart_type = 'line'


class AreaChart(Chart):
    chart_type = 'line'

    @classmethod
    def _build_option(cls, **kwargs: Any) -> dict[str, Any]:
        option = super()._build_option(**kwargs)
        option['series'] = [{**series, 'areaStyle': {}} for series in option['series']]
        return option


class PieChart(Chart):
    chart_type = 'pie'
    default_tooltip = {'trigger': 'item'}


class GaugeChart(Chart):
    chart_type = 'gauge'
    default_tooltip = {'trigger': 'item'}

    min: float = 0
    max: float = 100
    detail_formatter: str = '{value}'

    @classmethod
    def build_option_body(cls, value: float, name: str = '', **_kwargs: Any) -> dict[str, Any]:
        return {
            'series': [
                {
                    'name': name,
                    'min': cls.min,
                    'max': cls.max,
                    'detail': {'formatter': cls.detail_formatter},
                    'data': [{'value': value, 'name': name}],
                }
            ]
        }
