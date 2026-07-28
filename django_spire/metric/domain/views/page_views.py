from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib.auth.decorators import permission_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404
from django_glue import Glue

from django_spire.metric.domain import models
from django_spire.metric.domain.navigation import DomainNavigation

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest

from django.template.response import TemplateResponse


@permission_required('metric_domain.view_domain')
def detail_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    domain = get_object_or_404(models.Domain, pk=pk)
    subdomains = domain.subdomains.active()

    Glue.queryset(request, 'subdomains', subdomains, Glue.Access.CHANGE, fields='__all__')

    nav = DomainNavigation()
    nav.breadcrumbs.add(str(domain), None)
    context = nav.as_context()
    context['domain'] = domain
    context['subdomains'] = subdomains
    context['subdomain_count'] = subdomains.count()

    return TemplateResponse(
        request, context=context, template='django_spire/metric/domain/page/detail_page.html'
    )


@permission_required('metric_domain.view_domain')
def list_view(request: WSGIRequest) -> TemplateResponse:
    domains = models.Domain.objects.active()

    Glue.queryset(request, 'domains', domains, Glue.Access.CHANGE, fields='__all__')

    nav = DomainNavigation()
    context = nav.as_context()
    context['domains'] = domains
    context['domain_count'] = domains.count()

    return TemplateResponse(
        request, context=context, template='django_spire/metric/domain/page/list_page.html'
    )


@permission_required('metric_domain.view_subdomain')
def subdomain_detail_view(request: WSGIRequest, domain_pk: int, pk: int) -> TemplateResponse:
    subdomain = get_object_or_404(models.SubDomain, domain_id=domain_pk, pk=pk)

    nav = DomainNavigation()
    nav.page_title = str(subdomain)
    nav.breadcrumbs.add(
        name=str(subdomain.domain),
        view_name='django_spire:metric:domain:page:detail',
        view_kwargs={'pk': subdomain.domain.pk},
    )
    nav.breadcrumbs.add(
        name='Sub Domains',
        view_name='django_spire:metric:domain:page:detail',
        view_kwargs={'pk': domain_pk},
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
