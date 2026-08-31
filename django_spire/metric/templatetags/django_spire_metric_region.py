from __future__ import annotations

from typing import TYPE_CHECKING

from django import template

from django_spire.metric.visual.constants import VISUAL_REGION_LIVE_UPDATE_INTERVAL
from django_spire.metric.visual.models import VisualRegion

if TYPE_CHECKING:
    from typing import Any


register = template.Library()


@register.inclusion_tag('django_spire/metric/visual/render/region_visual.html', takes_context=True)
def render_visual_region(context: dict[str, Any], key: str) -> dict[str, Any]:
    request = context.get('request')

    region = (
        VisualRegion.objects.select_related('visual__statistic')
        .prefetch_related('visual__conditions', 'visual__references')
        .for_key(key)
        .first()
    )

    if region is None or not region.visual_id or region.visual.is_deleted:
        return {
            'region': region,
            'visual': None,
            'display_title': region.services.transformation.display_title if region else key,
            'chart': None,
            'chart_glue_name': '',
            'chart_update_interval': 0,
        }

    render_context = region.visual.services.transformation.render_context()
    chart = render_context.get('chart')
    live = region.is_live_updated

    if chart is not None and live and request is not None:
        chart.glue(request)

    return {
        'region': region,
        'visual': render_context['visual'],
        'current_value': render_context['current_value'],
        'current_condition': render_context['current_condition'],
        'chart': chart,
        'display_title': region.services.transformation.display_title,
        'chart_glue_name': chart.glue_name if chart is not None and live else '',
        'chart_update_interval': VISUAL_REGION_LIVE_UPDATE_INTERVAL if live else 0,
        'period_start': render_context.get('period_start'),
        'period_end': render_context.get('period_end'),
    }
