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

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


@permission_required('domain_statistic.view_statistic')
def detail_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    statistic = get_object_or_404(models.Statistic, pk=pk)

    context_data = {'statistic': statistic}
    context_data['page_title'] = str(statistic)
    context_data['page_description'] = 'Detail View'
    context_data['breadcrumbs'] = [
        {'name': 'Statistics', 'href': reverse('metric:domain:statistic:page:list')},
        {'name': str(statistic), 'href': None},
    ]
    return TemplateResponse(
        request, context=context_data, template='metric/domain/statistic/page/detail_page.html'
    )


@permission_required('domain_statistic.view_statistic')
def list_view(request: WSGIRequest) -> TemplateResponse:
    models.Statistic.objects.process_session_filter(
        request=request, session_key=LIST_FILTERING_SESSION_KEY, form_class=StatisticListFilterForm
    )

    context_data = {
        'responsive_mode': 'scroll',
        'statistic_items_endpoint': reverse('metric:domain:statistic:template:items'),
        'filter_session': SessionController(request, LIST_FILTERING_SESSION_KEY),
        'page_title': 'Statistic',
        'page_description': 'List View',
        'breadcrumbs': [{'name': 'Statistics', 'href': None}],
    }

    return TemplateResponse(
        request, context=context_data, template='metric/domain/statistic/page/list_page.html'
    )
