from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib.auth.decorators import permission_required
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.urls import reverse
from django_glue import Glue

from django_spire.contrib.form.confirmation_forms import DeleteConfirmationForm
from django_spire.contrib.redirects import safe_redirect_url
from django_spire.contrib.shortcuts import get_object_or_null_obj
from django_spire.metric.domain.statistic import forms, models
from django_spire.metric.domain.statistic.navigation import (
    StatisticGroupNavigation,
    StatisticNavigation,
)

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


@permission_required('metric_domain.add_statisticgroup')
def group_create_view(request: WSGIRequest) -> TemplateResponse:
    return _group_form_view(request)


@permission_required('metric_domain.change_statisticgroup')
def group_update_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    return _group_form_view(request, pk)


@permission_required('metric_domain.delete_statisticgroup')
def group_delete_form_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    group = get_object_or_404(models.StatisticGroup, pk=pk)
    return_url = safe_redirect_url(
        request, fallback=reverse('django_spire:metric:domain:statistic:page:group_list')
    )

    form = DeleteConfirmationForm(request.POST, obj=group)

    if request.method == 'POST' and form.is_valid():
        group.set_deleted()
        group.add_activity(
            user=request.user,
            verb='deleted',
            information=f'{request.user.get_full_name()} deleted statistic group "{group}".',
        )
        return HttpResponseRedirect(return_url)

    nav = StatisticGroupNavigation()
    nav.page_title = f'Delete {group}'
    nav.breadcrumbs.add(
        name=str(group),
        view_name='django_spire:metric:domain:statistic:page:group_detail',
        view_kwargs={'pk': group.pk},
    )
    nav.breadcrumbs.add('Delete')
    context = nav.as_context()
    context['form_title'] = f'Delete {group}'
    context['form_description'] = (
        f'Are you sure you would like to delete statistic group "{group}"?'
    )
    context['return_url'] = return_url
    return TemplateResponse(
        request,
        context=context,
        template='django_spire/metric/domain/statistic/form/group_delete_confirmation_form_page.html',
    )


@permission_required('metric_domain.add_statistic')
def create_view(request: WSGIRequest) -> TemplateResponse:
    return _form_view(request)


@permission_required('metric_domain.change_statistic')
def update_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    return _form_view(request, pk)


@permission_required('metric_domain.delete_statistic')
def delete_form_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    statistic = get_object_or_404(models.Statistic, pk=pk)
    return_url = safe_redirect_url(
        request, fallback=reverse('django_spire:metric:domain:statistic:page:list')
    )

    form = DeleteConfirmationForm(request.POST, obj=statistic)

    if request.method == 'POST' and form.is_valid():
        statistic.set_deleted()
        statistic.add_activity(
            user=request.user,
            verb='deleted',
            information=f'{request.user.get_full_name()} deleted statistic "{statistic}".',
        )
        return HttpResponseRedirect(return_url)

    nav = StatisticNavigation()
    nav.page_title = f'Delete {statistic}'
    nav.breadcrumbs.add(
        name=str(statistic.group),
        view_name='django_spire:metric:domain:statistic:page:group_detail',
        view_kwargs={'pk': statistic.group.pk},
    )
    nav.breadcrumbs.add(str(statistic))
    nav.breadcrumbs.add('Delete')
    context = nav.as_context()
    context['form_title'] = f'Delete {statistic}'
    context['form_description'] = f'Are you sure you would like to delete statistic "{statistic}"?'
    context['return_url'] = return_url
    return TemplateResponse(
        request,
        context=context,
        template='django_spire/metric/domain/statistic/form/statistic_delete_confirmation_form_page.html',
    )


def _group_form_view(request: WSGIRequest, pk: int = 0) -> TemplateResponse:
    group = get_object_or_null_obj(models.StatisticGroup, pk=pk)

    nav = StatisticGroupNavigation()
    nav.page_title = str(group._meta.verbose_name.title())
    nav.page_description = 'Edit' if group.pk else 'Create'
    nav.breadcrumbs.add('Edit' if group.pk else 'Create')

    form = forms.StatisticGroupForm(request.POST or None, instance=group)

    Glue.form(request, 'group_form', form, Glue.Access.DELETE)

    return TemplateResponse(
        request,
        context=nav.as_context(),
        template='django_spire/metric/domain/statistic/page/group_form_page.html',
    )


def _form_view(request: WSGIRequest, pk: int = 0) -> TemplateResponse:
    statistic = get_object_or_null_obj(models.Statistic, pk=pk)

    nav = StatisticNavigation()
    nav.page_title = str(statistic._meta.verbose_name.title())
    nav.page_description = 'Edit' if statistic.pk else 'Create'
    nav.breadcrumbs.add('Edit' if statistic.pk else 'Create')

    form = forms.StatisticForm(request.POST or None, instance=statistic)

    Glue.form(request, 'statistic_form', form, Glue.Access.DELETE)

    return TemplateResponse(
        request,
        context=nav.as_context(),
        template='django_spire/metric/domain/statistic/page/statistic_form_page.html',
    )
