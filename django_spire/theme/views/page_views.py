from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib.auth.decorators import login_required
from django.template.response import TemplateResponse
from django.urls import reverse

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


@login_required()
def dashboard_view(request: WSGIRequest) -> TemplateResponse:
    return TemplateResponse(
        request,
        'django_spire/theme/page/dashboard_page.html',
        context={
            'page_title': 'Theme',
            'page_description': 'Dashboard',
            'breadcrumbs': [{'name': 'Dashboard', 'href': None}],
        },
    )


@login_required()
def colors_view(request: WSGIRequest) -> TemplateResponse:
    return TemplateResponse(
        request,
        'django_spire/theme/page/colors_page.html',
        context={
            'page_title': 'Theme',
            'page_description': 'Colors',
            'breadcrumbs': [
                {'name': 'Dashboard', 'href': reverse('django_spire:theme:page:dashboard')},
                {'name': 'Colors', 'href': None},
            ],
        },
    )


@login_required()
def django_glue_view(request: WSGIRequest) -> TemplateResponse:
    return TemplateResponse(
        request,
        'django_spire/theme/page/django_glue_page.html',
        context={
            'page_title': 'Theme',
            'page_description': 'Django Glue',
            'breadcrumbs': [
                {'name': 'Dashboard', 'href': reverse('django_spire:theme:page:dashboard')},
                {'name': 'Django Glue', 'href': None},
            ],
        },
    )


@login_required()
def example_view(request: WSGIRequest) -> TemplateResponse:
    return TemplateResponse(
        request,
        'django_spire/theme/example/page/example_page.html',
        context={
            'page_title': 'Theme',
            'page_description': 'Core Templates',
            'breadcrumbs': [
                {'name': 'Dashboard', 'href': reverse('django_spire:theme:page:dashboard')},
                {'name': 'Core Templates', 'href': None},
            ],
        },
    )


@login_required()
def typography_view(request: WSGIRequest) -> TemplateResponse:
    return TemplateResponse(
        request,
        'django_spire/theme/page/typography_page.html',
        context={
            'page_title': 'Theme',
            'page_description': 'Typography',
            'breadcrumbs': [
                {'name': 'Dashboard', 'href': reverse('django_spire:theme:page:dashboard')},
                {'name': 'Typography', 'href': None},
            ],
        },
    )


@login_required()
def buttons_view(request: WSGIRequest) -> TemplateResponse:
    return TemplateResponse(
        request,
        'django_spire/theme/page/buttons_page.html',
        context={
            'page_title': 'Theme',
            'page_description': 'Buttons',
            'breadcrumbs': [
                {'name': 'Dashboard', 'href': reverse('django_spire:theme:page:dashboard')},
                {'name': 'Buttons', 'href': None},
            ],
        },
    )


@login_required()
def badges_view(request: WSGIRequest) -> TemplateResponse:
    return TemplateResponse(
        request,
        'django_spire/theme/page/badges_page.html',
        context={
            'page_title': 'Theme',
            'page_description': 'Badges',
            'breadcrumbs': [
                {'name': 'Dashboard', 'href': reverse('django_spire:theme:page:dashboard')},
                {'name': 'Badges', 'href': None},
            ],
        },
    )


@login_required()
def borders_view(request: WSGIRequest) -> TemplateResponse:
    return TemplateResponse(
        request,
        'django_spire/theme/page/borders_page.html',
        context={
            'page_title': 'Theme',
            'page_description': 'Borders',
            'breadcrumbs': [
                {'name': 'Dashboard', 'href': reverse('django_spire:theme:page:dashboard')},
                {'name': 'Borders', 'href': None},
            ],
        },
    )
