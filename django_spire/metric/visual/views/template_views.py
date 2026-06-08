from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib.auth.decorators import permission_required
from django.template.response import TemplateResponse

from django_spire.metric.visual import models
from django_spire.metric.visual.constants import LIST_FILTERING_SESSION_KEY
from django_spire.metric.visual.forms import VisualListFilterForm

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


@permission_required('metric_visual.view_visual')
def items_view(request: WSGIRequest) -> TemplateResponse:
    sort_field = request.GET.get('sort', 'name')
    sort_direction = request.GET.get('direction', 'asc')

    visuals = models.Visual.objects.process_session_filter(
        request=request, session_key=LIST_FILTERING_SESSION_KEY, form_class=VisualListFilterForm
    ).order_by(f'{"-" if sort_direction == "desc" else ""}{sort_field}')

    batch_size = int(request.GET.get('batch_size', 10))
    page = int(request.GET.get('page', 1))
    total_count = visuals.count()
    start = (page - 1) * batch_size
    end = start + batch_size
    items = list(visuals[start:end])
    context = {
        'visuals': items,
        'has_next': total_count > end,
        'total_count': total_count,
        'batch_size': batch_size,
    }
    return TemplateResponse(request, 'metric/visual/table/rows.html', context=context)
