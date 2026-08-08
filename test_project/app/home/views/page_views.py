from __future__ import annotations

from typing import TYPE_CHECKING

from django.template.response import TemplateResponse
from django_glue import Glue

from django_spire.contrib.chart.charts import BarChart

from test_project.app.home.chart_data import MONTHS, PRODUCTS
from test_project.app.home.navigation import HomeNavigation

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


def home_view(request: WSGIRequest) -> TemplateResponse:
    nav = HomeNavigation()
    nav.page_title = 'Test Project Landing'
    nav.breadcrumbs.add('Welcome')

    return TemplateResponse(request, template='home/page/home_page.html', context=nav.as_context())


def markdown_demo_view(request: WSGIRequest) -> TemplateResponse:
    nav = HomeNavigation()
    nav.page_title = 'Markdown Demo'
    nav.breadcrumbs.add('Home', '/')
    nav.breadcrumbs.add('Markdown Demo')

    return TemplateResponse(
        request, template='home/page/markdown_demo_page.html', context=nav.as_context()
    )


def chart_demo_view(request: WSGIRequest) -> TemplateResponse:
    nav = HomeNavigation()
    nav.page_title = 'Chart Demo'
    nav.breadcrumbs.add('Home', '/')
    nav.breadcrumbs.add('Chart Demo')

    static_chart = BarChart(title='Static Monthly Sales')
    static_chart.set_categories(MONTHS)
    static_chart.add_series(
        PRODUCTS[0], [120, 200, 150, 80, 170, 210, 190, 230, 260, 240, 280, 300]
    )
    static_chart.add_series(
        PRODUCTS[1], [90, 110, 130, 160, 120, 140, 170, 150, 180, 200, 220, 190]
    )

    dynamic_chart = BarChart(title='Dynamic Monthly Sales')
    dynamic_chart.set_categories(MONTHS)
    dynamic_chart.add_series(
        PRODUCTS[0], [120, 200, 150, 80, 170, 210, 190, 230, 260, 240, 280, 300]
    )
    dynamic_chart.add_series(
        PRODUCTS[1], [90, 110, 130, 160, 120, 140, 170, 150, 180, 200, 220, 190]
    )

    Glue.function(
        request, 'monthly_sales_chart', 'test_project.app.home.chart_data.monthly_sales_chart_data'
    )

    return TemplateResponse(
        request,
        template='home/page/chart_demo_page.html',
        context={**nav.as_context(), 'static_chart': static_chart, 'dynamic_chart': dynamic_chart},
    )
