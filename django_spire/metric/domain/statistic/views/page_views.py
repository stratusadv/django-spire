from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib.auth.decorators import permission_required
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.urls import reverse

from django_spire.contrib.session.controller import SessionController


from django_spire.metric.domain.statistic import models
from django_spire.metric.domain.statistic.forms import StatisticListFilterForm
from django_spire.metric.domain.statistic.constants import LIST_FILTERING_SESSION_KEY
from django_spire.metric.domain.statistic.navigation import StatisticNavigation

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


@permission_required('domain_statistic.view_statistic')
def detail_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    statistic = get_object_or_404(models.Statistic, pk=pk)

    nav = StatisticNavigation()
    nav.page_title = str(statistic)
    nav.page_description = 'Detail View'
    nav.breadcrumbs.add('Statistics', 'metric:domain:statistic:page:list')
    nav.breadcrumbs.add(str(statistic))
    context = nav.as_context()
    context['statistic'] = statistic
    return TemplateResponse(
        request, context=context, template='metric/domain/statistic/page/detail_page.html'
    )


@permission_required('domain_statistic.view_statistic')
def list_view(request: WSGIRequest) -> TemplateResponse:
    models.Statistic.objects.process_session_filter(
        request=request, session_key=LIST_FILTERING_SESSION_KEY, form_class=StatisticListFilterForm
    )

    nav = StatisticNavigation()
    nav.page_title = 'Statistic'
    nav.page_description = 'List View'
    nav.breadcrumbs.add('Statistics')
    context = nav.as_context()
    context['responsive_mode'] = 'scroll'
    context['statistic_items_endpoint'] = reverse('metric:domain:statistic:template:items')
    context['filter_session'] = SessionController(request, LIST_FILTERING_SESSION_KEY)
    return TemplateResponse(
        request, context=context, template='metric/domain/statistic/page/list_page.html'
    )
