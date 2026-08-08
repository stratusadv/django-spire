from __future__ import annotations

import random

from django_spire.contrib.chart.charts import BarChart

MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
PRODUCTS = ['Product A', 'Product B']


def monthly_sales_chart_data() -> dict:
    chart = BarChart(title='Monthly Sales')
    chart.set_categories(MONTHS)

    for product in PRODUCTS:
        chart.add_series(product, [random.randint(80, 320) for _ in MONTHS])

    return chart.to_option_dict()
