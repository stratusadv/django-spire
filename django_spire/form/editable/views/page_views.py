from __future__ import annotations

from typing_extensions import TYPE_CHECKING

from django.contrib.auth.decorators import login_required

from django_spire.contrib import Breadcrumbs
from django_spire.contrib.generic_views import portal_views

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest
    from django.template.response import TemplateResponse


@login_required()
def dashboard_view(request: WSGIRequest) -> TemplateResponse:
    crumbs = Breadcrumbs()
    crumbs.add_breadcrumb('Dashboard')

    return portal_views.template_view(
        request,
        page_title='Form',
        page_description='Dashboard',
        breadcrumbs=crumbs,
        template='django_spire/form/editable/page/dashboard_page.html'
    )
