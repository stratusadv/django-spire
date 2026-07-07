from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib.auth.decorators import permission_required
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.urls import reverse

from django_spire.contrib.form.confirmation_forms import DeleteConfirmationForm
from django_spire.contrib.form.tools import show_form_errors
from django_spire.contrib.redirects import safe_redirect_url
from django_spire.contrib.shortcuts import get_object_or_null_obj
from django_spire.history.activity.utils import add_form_activity

from django_glue import Glue

from django_spire.metric.domain import forms, models
from django_spire.metric.domain.navigation import DomainNavigation

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


@permission_required('metric_domain.delete_domain')
def delete_modal_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    domain = get_object_or_404(models.Domain, pk=pk)

    form_action = reverse('metric:domain:form:delete_modal', kwargs={'pk': pk})
    fallback = reverse('metric:domain:page:list')
    return_url = safe_redirect_url(request, fallback=fallback)

    if request.method == 'POST':
        form = DeleteConfirmationForm(data=request.POST, obj=domain)

        if form.is_valid():
            if form.cleaned_data['should_delete']:
                domain.add_activity(
                    user=request.user,
                    verb='deleted',
                    information=f'{request.user.get_full_name()} deleted a domain.',
                )
                domain.set_deleted()

            return HttpResponseRedirect(return_url)
    else:
        form = DeleteConfirmationForm(obj=domain)

    nav = DomainNavigation()
    nav.page_title = 'Delete Domain'
    context = nav.as_context()
    context['form'] = form
    context['form_title'] = 'Delete Domain'
    context['form_description'] = f'Are you sure you would like to delete domain "{domain}"?'
    context['form_action'] = form_action

    return TemplateResponse(
        request,
        'django_spire/contrib/page/../../../core/templates/django_spire/page/delete_confirmation_form_page.html', context
    )


@permission_required('metric_domain.delete_domain')
def delete_form_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    domain = get_object_or_404(models.Domain, pk=pk)
    return_url = request.GET.get('return_url', reverse('metric:domain:page:list'))

    if request.method == 'POST':
        form = DeleteConfirmationForm(data=request.POST, obj=domain)

        if form.is_valid():
            if form.cleaned_data['should_delete']:
                domain.set_deleted()
                domain.add_activity(
                    user=request.user,
                    verb='deleted',
                    information=f'{request.user.get_full_name()} deleted domain "{domain}".',
                )

            return HttpResponseRedirect(return_url)
    else:
        form = DeleteConfirmationForm(obj=domain)

    nav = DomainNavigation()
    nav.page_title = 'Delete Domain'
    nav.breadcrumbs.add('Domains', 'metric:domain:page:list')
    nav.breadcrumbs.add(str(domain))
    nav.breadcrumbs.add('Delete')
    context = nav.as_context()
    context['form'] = form
    context['form_title'] = f'Delete {domain}'
    context['form_description'] = f'Are you sure you would like to delete domain "{domain}"?'

    return TemplateResponse(
        request,
        'django_spire/contrib/page/../../../core/templates/django_spire/page/delete_confirmation_form_page.html', context
    )


@permission_required('metric_domain.add_domain')
def create_modal_view(request: WSGIRequest) -> TemplateResponse:
    return _modal_view(request)


@permission_required('metric_domain.change_domain')
def update_modal_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    return _modal_view(request, pk)


def _modal_view(request: WSGIRequest, pk: int = 0) -> TemplateResponse:
    domain = get_object_or_404(models.Domain, pk=pk)

    Glue.model(request, 'domain', domain)

    context_data = {'domain': domain}

    return TemplateResponse(
        request, context=context_data, template='metric/domain/modal/content/form.html'
    )


@permission_required('metric_domain.add_domain')
def create_view(request: WSGIRequest) -> TemplateResponse:
    return _form_view(request)


@permission_required('metric_domain.change_domain')
def update_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    return _form_view(request, pk)


def _form_view(request: WSGIRequest, pk: int = 0) -> TemplateResponse | HttpResponseRedirect:
    domain = get_object_or_null_obj(models.Domain, pk=pk)

    Glue.model(request, 'domain', domain, 'view')

    if request.method == 'POST':
        form = forms.DomainForm(request.POST, instance=domain)

        if form.is_valid():
            domain, _ = domain.services.save_model_obj(**form.cleaned_data)
            add_form_activity(domain, pk, request.user)

            return redirect(request.GET.get('return_url', reverse('metric:domain:page:list')))

        show_form_errors(request, form)
    else:
        form = forms.DomainForm(instance=domain)

    nav = DomainNavigation()
    nav.page_title = str(domain._meta.verbose_name.title())
    nav.breadcrumbs.add('Domains', 'metric:domain:page:list')
    nav.breadcrumbs.add('Edit' if domain.pk else 'Create')
    context = nav.as_context()
    context['form'] = form
    context['form_title'] = str(domain._meta.verbose_name.title())
    context['form_description'] = 'Edit' if domain.pk else 'Create'

    return TemplateResponse(request, 'metric/domain/page/form_page.html', context)
