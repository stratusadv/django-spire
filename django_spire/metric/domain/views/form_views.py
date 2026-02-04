from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib.auth.decorators import permission_required
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.urls import reverse

from django_spire.contrib.form.utils import show_form_errors
from django_spire.contrib.generic_views import modal_views, portal_views
from django_spire.core.redirect.safe_redirect import safe_redirect_url
from django_spire.core.shortcuts import get_object_or_null_obj
from django_spire.history.activity.utils import add_form_activity

import django_glue as dg

from django_spire.metric.domain import forms, models

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest
    from django.http import HttpResponseRedirect


@permission_required('metric_domain.delete_domain')
def delete_modal_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    domain = get_object_or_404(models.Domain, pk=pk)

    form_action = reverse(
        'metric:domain:form:delete_modal',
        kwargs={'pk': pk}
    )

    def add_activity() -> None:
        domain.add_activity(
            user=request.user,
            verb='deleted',
            information=f'{request.user.get_full_name()} deleted a domain.'
        )

    fallback = reverse('metric:domain:page:list')
    return_url = safe_redirect_url(request, fallback=fallback)

    return modal_views.dispatch_modal_delete_form_content(
        request,
        obj=domain,
        form_action=form_action,
        activity_func=add_activity,
        return_url=return_url,
    )


@permission_required('metric_domain.delete_domain')
def delete_form_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    domain = get_object_or_404(models.Domain, pk=pk)

    return_url = request.GET.get(
        'return_url',
        reverse('metric:domain:page:list')
    )

    return portal_views.delete_form_view(
        request,
        obj=domain,
        return_url=return_url
    )


@permission_required('metric_domain.add_domain')
def create_modal_view(request: WSGIRequest) -> TemplateResponse:
    return _modal_view(request)


@permission_required('metric_domain.change_domain')
def update_modal_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    return _modal_view(request, pk)


def _modal_view(request: WSGIRequest, pk: int = 0) -> TemplateResponse:
    domain = get_object_or_404(models.Domain, pk=pk)

    dg.glue_model_object(request, 'domain', domain)

    context_data = {
        'domain': domain
    }

    return TemplateResponse(
        request,
        context=context_data,
        template='metric/domain/modal/content/form.html'
    )


@permission_required('metric_domain.add_domain')
def create_view(request: WSGIRequest) -> TemplateResponse:
    return _form_view(request)


@permission_required('metric_domain.change_domain')
def update_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    return _form_view(request, pk)


def _form_view(request: WSGIRequest, pk: int = 0) -> TemplateResponse|HttpResponseRedirect:
    domain = get_object_or_null_obj(models.Domain, pk=pk)

    dg.glue_model_object(request, 'domain', domain, 'view')

    if request.method == 'POST':
        form = forms.DomainForm(request.POST, instance=domain)

        if form.is_valid():
            domain, _ = domain.services.save_model_obj(**form.cleaned_data)
            add_form_activity(domain, pk, request.user)

            return redirect(
                request.GET.get(
                    'return_url',
                    reverse('metric:domain:page:list')
                )
            )

        show_form_errors(request, form)
    else:
        form = forms.DomainForm(instance=domain)

    return portal_views.form_view(
        request,
        form=form,
        obj=domain,
        template='metric/domain/page/form_page.html'
    )
