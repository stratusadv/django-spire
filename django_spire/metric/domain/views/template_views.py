from __future__ import annotations

from django.contrib.auth.decorators import permission_required
from django.template.response import TemplateResponse

from django_spire.metric.domain import models
from django_spire.metric.domain.constants import LIST_FILTERING_SESSION_KEY
from django_spire.metric.domain.forms import DomainListFilterForm


@permission_required('metric_domain.view_domain')
def items_view(request) -> TemplateResponse:  # noqa: ANN001
    sort_field = request.GET.get('sort', 'name')
    sort_direction = request.GET.get('direction', 'asc')

    domains = models.Domain.objects.process_session_filter(
        request=request, session_key=LIST_FILTERING_SESSION_KEY, form_class=DomainListFilterForm
    ).order_by(f'{"-" if sort_direction == "desc" else ""}{sort_field}')

    batch_size = int(request.GET.get('batch_size', 10))
    page = int(request.GET.get('page', 1))
    total_count = domains.count()
    start = (page - 1) * batch_size
    end = start + batch_size
    items = list(domains[start:end])
    context = {
        'domains': items,
        'has_next': total_count > end,
        'total_count': total_count,
        'batch_size': batch_size,
    }
    return TemplateResponse(request, 'metric/domain/table/rows.html', context=context)
