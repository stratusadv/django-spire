from __future__ import annotations

import random

from django_spire.contrib.chart.charts import AreaChart, BarChart, PieChart

MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
PRODUCTS = ['Product A', 'Product B']

STATIC_SERIES = [
    {'name': PRODUCTS[0], 'data': [120, 200, 150, 80, 170, 210, 190, 230, 260, 240, 280, 300]},
    {'name': PRODUCTS[1], 'data': [90, 110, 130, 160, 120, 140, 170, 150, 180, 200, 220, 190]},
]


class HomeStaticBarChart(BarChart):
    title = 'Static Monthly Sales'

    @classmethod
    def build_option_body(cls) -> dict:
        return {'xAxis': {'data': MONTHS}, 'series': STATIC_SERIES}


class HomeBarChart(BarChart):
    title = 'Monthly Sales'
    glue_name = 'monthly_sales_chart'

    @classmethod
    def build_option_body(cls, max_value: int = 320) -> dict:
        return {
            'xAxis': {'data': MONTHS},
            'series': [
                {'name': product, 'data': [random.randint(80, max_value) for _ in MONTHS]}
                for product in PRODUCTS
            ],
        }


class HomePieChart(PieChart):
    title = 'Sales by Product'

    @classmethod
    def build_option_body(cls) -> dict:
        return {
            'series': [
                {
                    'name': 'Sales',
                    'data': [
                        {'name': 'Product A', 'value': 335},
                        {'name': 'Product B', 'value': 548},
                        {'name': 'Product C', 'value': 234},
                        {'name': 'Product D', 'value': 197},
                    ],
                }
            ]
        }


class HomeAreaChart(AreaChart):
    title = 'Weekly Productivity Trend'
    glue_name = 'productivity_area_chart'

    @classmethod
    def build_option_body(cls) -> dict:
        return {
            'xAxis': {'data': MONTHS},
            'series': [{'name': 'Productivity', 'data': [random.randint(40, 160) for _ in MONTHS]}],
        }
