from __future__ import annotations

import functools

from typing import TYPE_CHECKING

from django.contrib.auth.decorators import (
    login_required as django_login_required,
    permission_required as django_permission_required,
)
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.views.decorators.http import require_POST

from django_spire.auth.permissions.decorators import permission_required

from test_project.app.home.charts import (
    HomeAreaChart,
    HomeBarChart,
    HomePieChart,
    HomeStaticBarChart,
)
from test_project.app.home.models import HomeExample
from test_project.app.home.navigation import HomeNavigation

if TYPE_CHECKING:
    from typing import Callable

    from django.core.handlers.wsgi import WSGIRequest


def example_object_required(view_func: Callable[..., HttpResponse]) -> Callable[..., HttpResponse]:
    """
    A decorator that fetches an object before the view runs.

    This decorator exists as matrix self-test surface: it mimics a client
    project's object-level decorator stacked above a permission gate, where
    the object fetch answers 404 before the gate is reached.
    """

    @functools.wraps(view_func)
    def wrapper(request: WSGIRequest, *args, **kwargs) -> HttpResponse:
        get_object_or_404(HomeExample, pk=kwargs['pk'])

        return view_func(request, *args, **kwargs)

    return wrapper


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


# The restricted views below are the permission matrix's self-test surface,
# audited by django_spire/testing/tests/test_permissions.py. Each one covers
# a gate shape: a plain spire gate, an object decorator over a spire gate, a
# POST-only spire gate, a Django login gate, and a Django permission gate.
@permission_required('test_project_home.view_homeexample')
def restricted_view(_request: WSGIRequest) -> HttpResponse:
    return HttpResponse('restricted')


@example_object_required
@permission_required('test_project_home.view_homeexample')
def restricted_detail_view(_request: WSGIRequest, pk: int) -> HttpResponse:
    return HttpResponse(f'restricted detail {pk}')


@require_POST
@permission_required('test_project_home.change_homeexample')
def restricted_submit_view(_request: WSGIRequest) -> HttpResponse:
    return HttpResponse('restricted submit')


@django_login_required
def restricted_django_login_view(_request: WSGIRequest) -> HttpResponse:
    return HttpResponse('restricted django login')


@django_permission_required('test_project_home.view_homeexample')
def restricted_django_permission_view(_request: WSGIRequest) -> HttpResponse:
    return HttpResponse('restricted django permission')
