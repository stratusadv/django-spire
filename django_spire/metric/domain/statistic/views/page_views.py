from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib.auth.decorators import permission_required
from django.shortcuts import get_object_or_404
from django.urls import reverse

from django_spire.contrib.generic_views import portal_views
from django_spire.core.table.enums import ResponsiveMode
from django_spire.contrib.session.controller import SessionController


from django_spire.metric.domain.statistic import models
from django_spire.metric.domain.statistic.forms import StatisticListFilterForm
from django_spire.metric.domain.statistic.constants import LIST_FILTERING_SESSION_KEY

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest
    from django.template.response import TemplateResponse


@permission_required('domain_statistic.view_statistic')
def detail_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    statistic = get_object_or_404(models.Statistic, pk=pk)

    context_data = {
        'statistic': statistic,
    }

    return portal_views.detail_view(
        request,
        obj=statistic,
        context_data=context_data,
        template='metric/domain/statistic/page/detail_page.html'
    )


@permission_required('domain_statistic.view_statistic')
def list_view(request: WSGIRequest) -> TemplateResponse:
    models.Statistic.objects.process_session_filter(
        request=request,
        session_key=LIST_FILTERING_SESSION_KEY,
        form_class=StatisticListFilterForm,
    )

    context_data = {
        'responsive_mode': ResponsiveMode.SCROLL,
        'statistic_items_endpoint': reverse('metric:domain:statistic:template:items'),
        'filter_session': SessionController(request, LIST_FILTERING_SESSION_KEY),
    }

    return portal_views.list_view(
        request,
        model=models.Statistic,
        context_data=context_data,
        template='metric/domain/statistic/page/list_page.html'
    )
