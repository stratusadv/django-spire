from __future__ import annotations

from django.contrib.auth.decorators import permission_required
from django.template.response import TemplateResponse

from django_spire.metric.domain.statistic import models
from django_spire.metric.domain.statistic.constants import LIST_FILTERING_SESSION_KEY
from django_spire.metric.domain.statistic.forms import StatisticListFilterForm


@permission_required('domain_statistic.view_statistic')
def items_view(request) -> TemplateResponse:  # noqa: ANN001
    sort_field = request.GET.get('sort', 'name')
    sort_direction = request.GET.get('direction', 'asc')

    statistics = models.Statistic.objects.process_session_filter(
        request=request, session_key=LIST_FILTERING_SESSION_KEY, form_class=StatisticListFilterForm
    ).order_by(f'{"-" if sort_direction == "desc" else ""}{sort_field}')

    batch_size = int(request.GET.get('batch_size', 10))
    page = int(request.GET.get('page', 1))
    total_count = statistics.count()
    start = (page - 1) * batch_size
    end = start + batch_size
    items = list(statistics[start:end])
    context = {
        'statistics': items,
        'has_next': total_count > end,
        'total_count': total_count,
        'batch_size': batch_size,
    }
    return TemplateResponse(request, 'metric/domain/statistic/table/rows.html', context=context)
