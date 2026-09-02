from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib.auth.decorators import permission_required
from django.template.response import TemplateResponse

from django_spire.metric.domain.statistic import models

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest

SORT_FIELDS = ('name', 'created_datetime', 'is_active', 'key')


@permission_required('django_spire_metric_domain.view_statistic')
def items_view(request: WSGIRequest) -> TemplateResponse:
    sort_field = request.GET.get('sort', 'name')
    if sort_field not in SORT_FIELDS:
        sort_field = 'name'

    sort_direction = request.GET.get('direction', 'asc')
    if sort_direction not in ('asc', 'desc'):
        sort_direction = 'asc'

    try:
        batch_size = int(request.GET.get('batch_size', 10))
        page = int(request.GET.get('page', 1))
    except ValueError:
        batch_size = 10
        page = 1

    batch_size = max(batch_size, 1)
    page = max(page, 1)

    statistics = (
        models.Statistic.objects.active()
        .not_deleted()
        .bulk_filter(filter_data=request.GET.dict())
        .select_related('group__domain')
        .order_by(f'{"-" if sort_direction == "desc" else ""}{sort_field}')
    )

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
    return TemplateResponse(
        request, 'django_spire/metric/domain/statistic/table/rows.html', context=context
    )
