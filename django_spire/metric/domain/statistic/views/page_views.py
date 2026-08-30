from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib.auth.decorators import permission_required
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.urls import reverse
from django_glue import Glue

from django_spire.constants import BASE_URL_NAME
from django_spire.metric.domain.statistic import models
from django_spire.metric.domain.statistic.constants import STATISTIC_VALUE_COUNT_MAX
from django_spire.metric.domain.statistic.navigation import (
    StatisticGroupNavigation,
    StatisticNavigation,
)

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


@permission_required('django_spire_metric_domain.view_statisticgroup')
def group_list_view(request: WSGIRequest) -> TemplateResponse:
    groups = models.StatisticGroup.objects.active().not_deleted().select_related('domain')

    Glue.queryset(request, 'groups', groups, Glue.Access.CHANGE, fields='__all__')

    nav = StatisticGroupNavigation()
    context = nav.as_context()
    context['groups'] = groups
    return TemplateResponse(
        request,
        context=context,
        template='django_spire/metric/domain/statistic/page/group_list_page.html',
    )


@permission_required('django_spire_metric_domain.view_statisticgroup')
def group_detail_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    group = get_object_or_404(models.StatisticGroup.objects.select_related('domain'), pk=pk)

    nav = StatisticGroupNavigation()
    nav.page_title = str(group)
    nav.breadcrumbs.add(str(group))
    context = nav.as_context()
    context['group'] = group
    context['statistics'] = group.statistics.active().not_deleted()
    return TemplateResponse(
        request,
        context=context,
        template='django_spire/metric/domain/statistic/page/group_detail_page.html',
    )


@permission_required('django_spire_metric_domain.view_statistic')
def detail_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    statistic = get_object_or_404(models.Statistic.objects.select_related('group__domain'), pk=pk)

    nav = StatisticNavigation()
    nav.page_title = str(statistic)
    nav.breadcrumbs.add(
        name=str(statistic.group),
        view_name='django_spire:metric:domain:statistic:page:group_detail',
        view_kwargs={'pk': statistic.group.pk},
    )
    nav.breadcrumbs.add(str(statistic))
    record_path = reverse(
        f'{BASE_URL_NAME}:api_v1:record_value', kwargs={'statistic_key': str(statistic.key)}
    )

    context = nav.as_context()
    context['statistic'] = statistic
    context['visuals'] = statistic.visuals.active().not_deleted().order_by('name')
    context['sub_domains'] = statistic.group.domain.subdomains.active().order_by('name')
    context['record_path'] = record_path
    context['today_total'] = statistic.services.transformation.total_for_interval()
    context['values'] = statistic.services.transformation.values_for_interval().order_by(
        '-timestamp'
    )[:STATISTIC_VALUE_COUNT_MAX]
    return TemplateResponse(
        request,
        context=context,
        template='django_spire/metric/domain/statistic/page/detail_page.html',
    )


@permission_required('django_spire_metric_domain.view_statistic')
def list_view(request: WSGIRequest) -> TemplateResponse:
    statistics = (
        models.Statistic.objects.active()
        .not_deleted()
        .bulk_filter(filter_data=request.GET.dict())
        .select_related('group__domain')
        .order_by('name')
    )

    nav = StatisticNavigation()
    nav.page_title = 'Statistic'
    nav.page_description = 'List View'
    context = nav.as_context()
    context['statistics'] = statistics
    return TemplateResponse(
        request,
        context=context,
        template='django_spire/metric/domain/statistic/page/list_page.html',
    )
