from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib.auth.decorators import login_required
from django.template.response import TemplateResponse
from django.urls import reverse

from django_spire.theme.navigation import ThemeNavigation

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


@login_required()
def dashboard_view(request: WSGIRequest) -> TemplateResponse:
    nav = ThemeNavigation()
    nav.page_title = 'Theme'
    nav.page_description = 'Dashboard'
    nav.breadcrumbs.add_breadcrumb('Dashboard')
    context = nav.as_context()
    return TemplateResponse(request, 'django_spire/theme/page/dashboard_page.html', context=context)


@login_required()
def colors_view(request: WSGIRequest) -> TemplateResponse:
    nav = ThemeNavigation()
    nav.page_title = 'Theme'
    nav.page_description = 'Colors'
    nav.breadcrumbs.add_breadcrumb('Dashboard', reverse('django_spire:theme:page:dashboard'))
    nav.breadcrumbs.add_breadcrumb('Colors')
    context = nav.as_context()
    return TemplateResponse(request, 'django_spire/theme/page/colors_page.html', context=context)


@login_required()
def django_glue_view(request: WSGIRequest) -> TemplateResponse:
    nav = ThemeNavigation()
    nav.page_title = 'Theme'
    nav.page_description = 'Django Glue'
    nav.breadcrumbs.add_breadcrumb('Dashboard', reverse('django_spire:theme:page:dashboard'))
    nav.breadcrumbs.add_breadcrumb('Django Glue')
    context = nav.as_context()
    return TemplateResponse(
        request, 'django_spire/theme/page/django_glue_page.html', context=context
    )


@login_required()
def example_view(request: WSGIRequest) -> TemplateResponse:
    nav = ThemeNavigation()
    nav.page_title = 'Theme'
    nav.page_description = 'Core Templates'
    nav.breadcrumbs.add_breadcrumb('Dashboard', reverse('django_spire:theme:page:dashboard'))
    nav.breadcrumbs.add_breadcrumb('Core Templates')
    context = nav.as_context()
    return TemplateResponse(
        request, 'django_spire/theme/example/page/example_page.html', context=context
    )


@login_required()
def typography_view(request: WSGIRequest) -> TemplateResponse:
    nav = ThemeNavigation()
    nav.page_title = 'Theme'
    nav.page_description = 'Typography'
    nav.breadcrumbs.add_breadcrumb('Dashboard', reverse('django_spire:theme:page:dashboard'))
    nav.breadcrumbs.add_breadcrumb('Typography')
    context = nav.as_context()
    return TemplateResponse(
        request, 'django_spire/theme/page/typography_page.html', context=context
    )


@login_required()
def buttons_view(request: WSGIRequest) -> TemplateResponse:
    nav = ThemeNavigation()
    nav.page_title = 'Theme'
    nav.page_description = 'Buttons'
    nav.breadcrumbs.add_breadcrumb('Dashboard', reverse('django_spire:theme:page:dashboard'))
    nav.breadcrumbs.add_breadcrumb('Buttons')
    context = nav.as_context()
    return TemplateResponse(request, 'django_spire/theme/page/buttons_page.html', context=context)


@login_required()
def badges_view(request: WSGIRequest) -> TemplateResponse:
    nav = ThemeNavigation()
    nav.page_title = 'Theme'
    nav.page_description = 'Badges'
    nav.breadcrumbs.add_breadcrumb('Dashboard', reverse('django_spire:theme:page:dashboard'))
    nav.breadcrumbs.add_breadcrumb('Badges')
    context = nav.as_context()
    return TemplateResponse(request, 'django_spire/theme/page/badges_page.html', context=context)


@login_required()
def borders_view(request: WSGIRequest) -> TemplateResponse:
    nav = ThemeNavigation()
    nav.page_title = 'Theme'
    nav.page_description = 'Borders'
    nav.breadcrumbs.add_breadcrumb('Dashboard', reverse('django_spire:theme:page:dashboard'))
    nav.breadcrumbs.add_breadcrumb('Borders')
    context = nav.as_context()
    return TemplateResponse(request, 'django_spire/theme/page/borders_page.html', context=context)
