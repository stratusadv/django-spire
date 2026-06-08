from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib.auth.decorators import permission_required
from django.shortcuts import get_object_or_404
from django.urls import reverse

from django_spire.core.table.enums import ResponsiveMode
from django_spire.contrib.session.controller import SessionController


from django_spire.metric.domain import models
from django_spire.metric.domain.forms import DomainListFilterForm
from django_spire.metric.domain.constants import LIST_FILTERING_SESSION_KEY
from django_spire.metric.domain.navigation import DomainNavigation

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest

from django.template.response import TemplateResponse


@permission_required('metric_domain.view_domain')
def detail_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    domain = get_object_or_404(models.Domain, pk=pk)

    nav = DomainNavigation()
    nav.page_title = str(domain)
    nav.breadcrumbs.add_breadcrumb('Domains', reverse('metric:domain:page:list'))
    nav.breadcrumbs.add_breadcrumb(str(domain), None)
    context = nav.as_context()
    context['domain'] = domain

    return TemplateResponse(
        request, context=context, template='metric/domain/page/detail_page.html'
    )


@permission_required('metric_domain.view_domain')
def list_view(request: WSGIRequest) -> TemplateResponse:
    models.Domain.objects.process_session_filter(
        request=request, session_key=LIST_FILTERING_SESSION_KEY, form_class=DomainListFilterForm
    )

    nav = DomainNavigation()
    nav.page_title = 'Domains'
    nav.breadcrumbs.add_breadcrumb('Domains', None)
    context = nav.as_context()
    context['responsive_mode'] = ResponsiveMode.SCROLL
    context['domain_items_endpoint'] = reverse('metric:domain:template:items')
    context['filter_session'] = SessionController(request, LIST_FILTERING_SESSION_KEY)

    return TemplateResponse(request, context=context, template='metric/domain/page/list_page.html')
