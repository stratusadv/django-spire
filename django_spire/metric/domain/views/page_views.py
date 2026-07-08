from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib.auth.decorators import permission_required
from django.shortcuts import get_object_or_404

from django_spire.metric.domain import models
from django_spire.metric.domain.navigation import DomainNavigation

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest

from django.template.response import TemplateResponse


@permission_required('metric_domain.view_domain')
def detail_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    domain = get_object_or_404(models.Domain, pk=pk)

    nav = DomainNavigation()
    nav.breadcrumbs.add(str(domain), None)
    context = nav.as_context()
    context['domain'] = domain
    context['subdomains'] = domain.subdomains.active()

    return TemplateResponse(
        request, context=context, template='django_spire/metric/domain/page/detail_page.html'
    )


@permission_required('metric_domain.view_domain')
def list_view(request: WSGIRequest) -> TemplateResponse:
    nav = DomainNavigation()
    context = nav.as_context()
    context['responsive_mode'] = 'scroll'
    context['domains'] = models.Domain.objects.active()

    return TemplateResponse(
        request, context=context, template='django_spire/metric/domain/page/list_page.html'
    )


@permission_required('metric_domain.view_subdomain')
def subdomain_detail_view(request: WSGIRequest, domain_pk: int, pk: int) -> TemplateResponse:
    subdomain = get_object_or_404(models.SubDomain, domain_id=domain_pk, pk=pk)

    nav = DomainNavigation()
    nav.page_title = str(subdomain)
    nav.breadcrumbs.add(str(subdomain.domain), None)
    nav.breadcrumbs.add(
        name='Sub Domains',
        url='django_spire:metric:domain:page:detail',
        url_kwargs={'pk': domain_pk},
    )
    nav.breadcrumbs.add(str(subdomain), None)
    context = nav.as_context()
    context['subdomain'] = subdomain
    context['domain_pk'] = domain_pk

    return TemplateResponse(
        request,
        context=context,
        template='django_spire/metric/domain/page/subdomain_detail_page.html',
    )
