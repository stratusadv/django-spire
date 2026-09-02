from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.urls import reverse
from django_glue import Glue

from django_spire.contrib.form.confirmation_forms import DeleteConfirmationForm
from django_spire.contrib.redirects import safe_redirect_url
from django_spire.contrib.shortcuts import get_object_or_null_obj
from django_spire.metric.domain import forms, models
from django_spire.metric.domain.navigation import DomainNavigation

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


@login_required
def form_view(request: WSGIRequest, pk: int) -> TemplateResponse | HttpResponseRedirect:
    domain = get_object_or_null_obj(models.Domain, pk=pk)

    nav = DomainNavigation()
    nav.set_page_title_to_form_action_from_model_instance(domain)

    if domain.pk:
        nav.breadcrumbs.add(domain, view_name='django_spire:metric:domain:page:detail', view_kwargs={'pk': domain.pk})

    nav.breadcrumbs.add('Edit' if domain.pk else 'New Domain')

    form = forms.DomainForm(request.POST or None, instance=domain)

    Glue.form(request, 'domain_form', form, Glue.Access.DELETE)

    context = {**nav.as_context()}

    return TemplateResponse(
        request=request, context=context, template='django_spire/metric/domain/page/form_page.html'
    )


@permission_required('django_spire_metric_domain.delete_domain')
def delete_form_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    domain = get_object_or_404(models.Domain, pk=pk)
    return_url = safe_redirect_url(
        request, fallback=reverse('django_spire:metric:domain:page:list')
    )

    if request.method == 'POST':
        form = DeleteConfirmationForm(data=request.POST, obj=domain)

        if form.is_valid():
            domain.set_deleted()

            return HttpResponseRedirect(return_url)
    else:
        form = DeleteConfirmationForm(obj=domain)

    nav = DomainNavigation()
    nav.page_title = 'Delete Domain'
    nav.breadcrumbs.add(
        name=str(domain), view_name='django_spire:metric:domain:page:detail', view_kwargs={'pk': pk}
    )
    nav.breadcrumbs.add('Delete')
    context = nav.as_context()
    context['form'] = form
    context['form_title'] = f'Delete Domain "{domain}"'
    context['form_description'] = f'Are you sure you would like to delete domain "{domain}"?'

    return TemplateResponse(
        request, 'django_spire/metric/domain/form/delete_confirmation_form_page.html', context
    )


@login_required
def subdomain_form_view(
        request: WSGIRequest, domain_pk: int, pk: int
) -> TemplateResponse | HttpResponseRedirect:
    subdomain = get_object_or_null_obj(models.SubDomain, pk=pk)

    nav = DomainNavigation()
    nav.set_page_title_to_form_action_from_model_instance(subdomain)
    nav.breadcrumbs.add(
        name=str(get_object_or_404(models.Domain, pk=domain_pk)),
        view_name='django_spire:metric:domain:page:detail',
        view_kwargs={'pk': domain_pk},
    )

    if subdomain.pk:
        nav.breadcrumbs.add(
            subdomain,
            view_name='django_spire:metric:domain:page:subdomain_detail',
            view_kwargs={'domain_pk': domain_pk, 'pk': subdomain.pk},
        )

    nav.breadcrumbs.add('Edit' if subdomain.pk else 'New Sub Domain')

    subdomain.domain_id = domain_pk

    form = forms.SubDomainForm(request.POST or None, instance=subdomain)

    Glue.form(request, 'subdomain_form', form, Glue.Access.DELETE)

    context = {**nav.as_context()}

    return TemplateResponse(
        request=request,
        context=context,
        template='django_spire/metric/domain/page/subdomain_form_page.html',
    )


@permission_required('django_spire_metric_domain.delete_subdomain')
def delete_subdomain_form_view(request: WSGIRequest, domain_pk: int, pk: int) -> TemplateResponse:
    subdomain = get_object_or_404(models.SubDomain, domain_id=domain_pk, pk=pk)
    domain_detail_url = reverse('django_spire:metric:domain:page:detail', kwargs={'pk': domain_pk})
    return_url = safe_redirect_url(request, fallback=domain_detail_url)

    if request.method == 'POST':
        form = DeleteConfirmationForm(data=request.POST, obj=subdomain)

        if form.is_valid():
            subdomain.set_deleted()

            return HttpResponseRedirect(return_url)
    else:
        form = DeleteConfirmationForm(obj=subdomain)

    nav = DomainNavigation()
    nav.page_title = 'Delete Sub Domain'
    nav.breadcrumbs.add(
        name=str(subdomain.domain),
        view_name='django_spire:metric:domain:page:detail',
        view_kwargs={'pk': domain_pk},
    )
    nav.breadcrumbs.add(
        subdomain,
        view_name='django_spire:metric:domain:page:subdomain_detail',
        view_kwargs={'domain_pk': domain_pk, 'pk': subdomain.pk},
    )
    nav.breadcrumbs.add('Delete', None)
    context = nav.as_context()
    context['form'] = form
    context['form_title'] = f'Delete Sub Domain "{subdomain}"'
    context['form_description'] = f'Are you sure you would like to delete sub domain "{subdomain}"?'
    context['domain_pk'] = domain_pk

    return TemplateResponse(
        request,
        'django_spire/metric/domain/form/subdomain_delete_confirmation_form_page.html',
        context,
    )
