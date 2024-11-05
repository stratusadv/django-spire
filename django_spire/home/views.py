from __future__ import annotations

from typing_extensions import TYPE_CHECKING

from django.conf import settings
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import reverse

from django_spire.breadcrumb.models import Breadcrumbs
from django_spire.views import portal_views

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


def home_view(request: WSGIRequest) -> TemplateResponse:
    crumbs = Breadcrumbs()
    crumbs.add_breadcrumb(name='Home', href=reverse('home:home'))

    return portal_views.template_view(
        request,
        page_title='Home',
        page_description='Your Portal',
        breadcrumbs=crumbs,
        template='spire/home/page/home_page.html'
    )


def maintenance_mode_view(request: WSGIRequest) -> TemplateResponse | HttpResponseRedirect:
    if not settings.MAINTENANCE_MODE:
        return HttpResponseRedirect(
            request.GET.get(
                'next',
                reverse('home:home')
            )
        )

    return TemplateResponse(
        request,
        template='spire/home/page/maintenance_mode_page.html'
    )
