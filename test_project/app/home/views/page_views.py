from __future__ import annotations

from typing import TYPE_CHECKING

from django.template.response import TemplateResponse

from test_project.app.home.navigation import HomeNavigation

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


def home_view(request: WSGIRequest) -> TemplateResponse:
    nav = HomeNavigation()
    nav.page_title = 'Welcome'
    nav.breadcrumbs.add('Tacos')
    nav.breadcrumbs.add('Tacos')
    nav.breadcrumbs.add('Tacos')
    nav.breadcrumbs.add('Tacos')
    nav.breadcrumbs.add('Tacos')

    return TemplateResponse(request, template='home/page/home_page.html', context=nav.as_context())
