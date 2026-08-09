from __future__ import annotations

from typing import TYPE_CHECKING

from django.template.response import TemplateResponse

from test_project.app.home.charts import (
    HomeAreaChart,
    HomeBarChart,
    HomePieChart,
    HomeStaticBarChart,
)
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

    max_value = max(int(request.GET.get('max_value', 320)), 80)

    static_chart = HomeStaticBarChart()
    dynamic_chart = HomeBarChart(params={'max_value': max_value})
    dynamic_chart.glue(request)
    pie_chart = HomePieChart()
    area_chart = HomeAreaChart()
    area_chart.glue(request)

    return TemplateResponse(
        request,
        template='home/page/chart_demo_page.html',
        context={
            **nav.as_context(),
            'static_chart': static_chart,
            'dynamic_chart': dynamic_chart,
            'pie_chart': pie_chart,
            'area_chart': area_chart,
        },
    )
