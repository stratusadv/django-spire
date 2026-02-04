from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib.auth.decorators import permission_required

from django_spire.contrib.generic_views import portal_views

from django_spire.metric.domain.statistic import models
from django_spire.metric.domain.statistic.constants import LIST_FILTERING_SESSION_KEY
from django_spire.metric.domain.statistic.forms import StatisticListFilterForm

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest
    from django.template.response import TemplateResponse


@permission_required('domain_statistic.view_statistic')
def items_view(request: WSGIRequest) -> TemplateResponse:
    sort_field = request.GET.get('sort', 'name')
    sort_direction = request.GET.get('direction', 'asc')

    statistics = (
        models.Statistic.objects
        .process_session_filter(
            request=request,
            session_key=LIST_FILTERING_SESSION_KEY,
            form_class=StatisticListFilterForm,
        ).order_by(
            f"{'-' if sort_direction == 'desc' else ''}{sort_field}"
        )
    )

    return portal_views.infinite_scrolling_view(
        request,
        context_data={'batch_size': 10,},
        queryset=statistics,
        queryset_name='statistics',
        template='metric/domain/statistic/table/rows.html'
    )
