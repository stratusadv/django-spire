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

from django_spire.metric.domain.statistic import forms, models

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


@permission_required('domain_statistic.delete_statistic')
def delete_modal_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    statistic = get_object_or_404(models.Statistic, pk=pk)

    form_action = reverse('metric:domain:statistic:form:delete_modal', kwargs={'pk': pk})
    fallback = reverse('metric:domain:statistic:page:list')
    return_url = safe_redirect_url(request, fallback=fallback)

    if request.method == 'POST':
        form = DeleteConfirmationForm(data=request.POST, obj=statistic)

        if form.is_valid():
            if form.cleaned_data['should_delete']:
                statistic.add_activity(
                    user=request.user,
                    verb='deleted',
                    information=f'{request.user.get_full_name()} deleted a statistic.',
                )
                statistic.set_deleted()

            return HttpResponseRedirect(return_url)
    else:
        form = DeleteConfirmationForm(obj=statistic)

    return TemplateResponse(
        request,
        context={
            'form': form,
            'form_title': 'Delete Statistic',
            'form_description': f'Are you sure you would like to delete statistic "{statistic}"?',
            'form_action': form_action,
            'django_spire_navigation': {'page_title': 'Delete Statistic'},
        },
        template='django_spire/page/delete_confirmation_form_page.html',
    )


@permission_required('domain_statistic.delete_statistic')
def delete_form_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    statistic = get_object_or_404(models.Statistic, pk=pk)
    return_url = request.GET.get('return_url', reverse('metric:domain:statistic:page:list'))

    if request.method == 'POST':
        form = DeleteConfirmationForm(data=request.POST, obj=statistic)

        if form.is_valid():
            if form.cleaned_data['should_delete']:
                statistic.set_deleted()
                statistic.add_activity(
                    user=request.user,
                    verb='deleted',
                    information=f'{request.user.get_full_name()} deleted statistic "{statistic}".',
                )

            return HttpResponseRedirect(return_url)
    else:
        form = DeleteConfirmationForm(obj=statistic)

    return TemplateResponse(
        request,
        context={
            'request': request,
            'form': form,
            'form_title': f'Delete {statistic}',
            'form_description': f'Are you sure you would like to delete statistic "{statistic}"?',
            'page_title': 'Delete Statistic',
            'breadcrumbs': [
                {'name': 'Statistics', 'href': reverse('metric:domain:statistic:page:list')},
                {'name': str(statistic), 'href': None},
                {'name': 'Delete', 'href': None},
            ],
        },
        template='django_spire/page/delete_confirmation_form_page.html',
    )


@permission_required('domain_statistic.add_statistic')
def create_modal_view(request: WSGIRequest) -> TemplateResponse:
    return _modal_view(request)


@permission_required('domain_statistic.change_statistic')
def update_modal_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    return _modal_view(request, pk)


def _modal_view(request: WSGIRequest, pk: int = 0) -> TemplateResponse:
    statistic = get_object_or_404(models.Statistic, pk=pk)

    Glue.model(request, 'statistic', statistic)

    context_data = {'request': request, 'statistic': statistic}

    return TemplateResponse(
        request, context=context_data, template='metric/domain/statistic/modal/content/form.html'
    )


@permission_required('domain_statistic.add_statistic')
def create_view(request: WSGIRequest) -> TemplateResponse:
    return _form_view(request)


@permission_required('domain_statistic.change_statistic')
def update_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    return _form_view(request, pk)


def _form_view(request: WSGIRequest, pk: int = 0) -> TemplateResponse | HttpResponseRedirect:
    statistic = get_object_or_null_obj(models.Statistic, pk=pk)

    Glue.model(request, 'statistic', statistic, 'view')

    if request.method == 'POST':
        form = forms.StatisticForm(request.POST, instance=statistic)

        if form.is_valid():
            statistic, _ = statistic.services.save_model_obj(**form.cleaned_data)
            add_form_activity(statistic, pk, request.user)

            return redirect(
                request.GET.get('return_url', reverse('metric:domain:statistic:page:list'))
            )

        show_form_errors(request, form)
    else:
        form = forms.StatisticForm(instance=statistic)

    context = {
        'request': request,
        'form': form,
        'page_title': str(statistic._meta.verbose_name.title()),
        'page_description': 'Edit' if statistic.pk else 'Create',
        'breadcrumbs': [
            {'name': 'Statistics', 'href': reverse('metric:domain:statistic:page:list')},
            {'name': 'Edit' if statistic.pk else 'Create', 'href': None},
        ],
    }
    return TemplateResponse(request, 'metric/domain/statistic/page/form_page.html', context)
