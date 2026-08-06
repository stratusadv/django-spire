from __future__ import annotations

from django.contrib.auth.decorators import permission_required
from django.template.response import TemplateResponse

from django_spire.metric.domain.statistic import models


@permission_required('metric_domain.view_statistic')
def items_view(request) -> TemplateResponse:  # noqa: ANN001
    sort_field = request.GET.get('sort', 'name')
    sort_direction = request.GET.get('direction', 'asc')

    statistics = (
        models.Statistic.objects.active()
        .not_deleted()
        .bulk_filter(filter_data=request.GET.dict())
        .order_by(f'{"-" if sort_direction == "desc" else ""}{sort_field}')
    )

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
    return TemplateResponse(
        request, 'django_spire/metric/domain/statistic/table/rows.html', context=context
    )
