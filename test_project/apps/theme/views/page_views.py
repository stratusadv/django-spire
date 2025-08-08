from __future__ import annotations

from typing_extensions import TYPE_CHECKING

from django.contrib.auth.decorators import permission_required
from django.template.response import TemplateResponse

from django_spire.contrib import Breadcrumbs
from django_spire.contrib.generic_views import portal_views


if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


@permission_required('apps.view_theme')
def dashboard_view(request: WSGIRequest) -> TemplateResponse:
    crumbs = Breadcrumbs()
    crumbs.add_breadcrumb('Dashboard')

    return portal_views.template_view(
        request,
        page_title='Theme',
        page_description='Dashboard',
        breadcrumbs=crumbs,
        template='theme/page/dashboard_page.html'
    )


@permission_required('apps.view_theme')
def colors_view(request: WSGIRequest) -> TemplateResponse:
    crumbs = Breadcrumbs()
    crumbs.add_breadcrumb('Dashboard', 'theme:page:dashboard')
    crumbs.add_breadcrumb('Colors')

    return portal_views.template_view(
        request,
        page_title='Theme',
        page_description='Colors',
        breadcrumbs=crumbs,
        template='theme/page/colors_page.html'
    )


@permission_required('apps.view_theme')
def typography_view(request: WSGIRequest) -> TemplateResponse:
    crumbs = Breadcrumbs()
    crumbs.add_breadcrumb('Dashboard', 'theme:page:dashboard')
    crumbs.add_breadcrumb('Typography')

    return portal_views.template_view(
        request,
        page_title='Theme',
        page_description='Typography',
        breadcrumbs=crumbs,
        template='theme/page/typography_page.html'
    )


@permission_required('apps.view_theme')
def buttons_view(request: WSGIRequest) -> TemplateResponse:
    crumbs = Breadcrumbs()
    crumbs.add_breadcrumb('Dashboard', 'theme:page:dashboard')
    crumbs.add_breadcrumb('Buttons')

    return portal_views.template_view(
        request,
        page_title='Theme',
        page_description='Buttons',
        breadcrumbs=crumbs,
        template='theme/page/buttons_page.html'
    )


@permission_required('apps.view_theme')
def badges_view(request: WSGIRequest) -> TemplateResponse:
    crumbs = Breadcrumbs()
    crumbs.add_breadcrumb('Dashboard', 'theme:page:dashboard')
    crumbs.add_breadcrumb('Badges')

    return portal_views.template_view(
        request,
        page_title='Theme',
        page_description='Badges',
        breadcrumbs=crumbs,
        template='theme/page/badges_page.html'
    )


@permission_required('apps.view_theme')
def borders_view(request: WSGIRequest) -> TemplateResponse:
    crumbs = Breadcrumbs()
    crumbs.add_breadcrumb('Dashboard', 'theme:page:dashboard')
    crumbs.add_breadcrumb('Borders')

    return portal_views.template_view(
        request,
        page_title='Theme',
        page_description='Borders',
        breadcrumbs=crumbs,
        template='theme/page/borders_page.html'
    )
