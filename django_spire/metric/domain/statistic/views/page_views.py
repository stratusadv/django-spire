from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib.auth.decorators import permission_required
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse

from django_spire.metric.domain.statistic import models
from django_spire.metric.domain.statistic.forms import StatisticListFilterForm
from django_spire.metric.domain.statistic.navigation import (
    StatisticGroupNavigation,
    StatisticNavigation,
)

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


@permission_required('metric_domain.view_statisticgroup')
def group_list_view(request: WSGIRequest) -> TemplateResponse:
    groups = (
        models.StatisticGroup.objects.active()
        .not_deleted()
        .bulk_filter(filter_data=request.GET.dict())
        .order_by('name')
    )

    nav = StatisticGroupNavigation()
    context = nav.as_context()
    context['groups'] = groups
    return TemplateResponse(
        request,
        context=context,
        template='django_spire/metric/domain/statistic/page/group_list_page.html',
    )


@permission_required('metric_domain.view_statisticgroup')
def group_detail_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    group = get_object_or_404(models.StatisticGroup, pk=pk)

    nav = StatisticGroupNavigation()
    nav.page_title = str(group)
    nav.page_description = 'Detail View'
    nav.breadcrumbs.add(str(group))
    context = nav.as_context()
    context['group'] = group
    context['statistics'] = group.statistics.active().not_deleted()
    return TemplateResponse(
        request,
        context=context,
        template='django_spire/metric/domain/statistic/page/group_detail_page.html',
    )


@permission_required('metric_domain.view_statistic')
def detail_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    statistic = get_object_or_404(models.Statistic, pk=pk)

    nav = StatisticNavigation()
    nav.page_title = str(statistic)
    nav.page_description = 'Detail View'
    nav.breadcrumbs.add(
        name=str(statistic.group),
        view_name='django_spire:metric:domain:statistic:page:group_detail',
        view_kwargs={'pk': statistic.group.pk},
    )
    nav.breadcrumbs.add(str(statistic))
    context = nav.as_context()
    context['statistic'] = statistic
    context['today_total'] = statistic.services.transformation.total_for_date()
    context['values'] = statistic.services.transformation.values_for_date()
    return TemplateResponse(
        request,
        context=context,
        template='django_spire/metric/domain/statistic/page/detail_page.html',
    )


@permission_required('metric_domain.view_statistic')
def list_view(request: WSGIRequest) -> TemplateResponse:
    statistics = (
        models.Statistic.objects.active()
        .not_deleted()
        .bulk_filter(filter_data=request.GET.dict())
        .order_by('name')
    )

    nav = StatisticNavigation()
    nav.page_title = 'Statistic'
    nav.page_description = 'List View'
    context = nav.as_context()
    context['statistics'] = statistics
    context['form'] = StatisticListFilterForm(request.GET)
    return TemplateResponse(
        request,
        context=context,
        template='django_spire/metric/domain/statistic/page/list_page.html',
    )
