from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from django.contrib.auth.decorators import permission_required
from django.contrib.contenttypes.models import ContentType
from django.db.models import Prefetch, Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django_glue import Glue

from django_spire.history.activity.models import Activity
from django_spire.metric.visual import models
from django_spire.metric.visual.navigation import VisualNavigation

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest

    from django.db.models import QuerySet

from django.template.response import TemplateResponse


def _browse_value_date(request: WSGIRequest) -> date | None:
    raw_value = request.GET.get('value_date')
    if not raw_value:
        return None

    try:
        value_date = date.fromisoformat(raw_value)
    except ValueError:
        return None

    if value_date > timezone.localdate():
        return None

    return value_date


def _visual_context(
    request: WSGIRequest, visual: models.Visual, value_date: date | None = None
) -> dict:
    transformation = visual.services.transformation
    period_start, period_end = transformation.display_window(value_date)
    no_match = transformation.no_matching_data()

    context = {
        'visual': visual,
        'current_value': transformation.current_value(value_date),
        'current_condition': None if no_match else transformation.current_condition(value_date),
        'no_matching_data': no_match,
        'period_start': period_start,
        'period_end': period_end,
        'display_unit_label': transformation.display_unit_label(),
    }

    chart = transformation.chart(value_date=value_date)
    if chart is not None:
        chart.glue(request)
        context['chart'] = chart

    return context


def _visual_activity_log(visual: models.Visual) -> QuerySet:
    condition_ct = ContentType.objects.get_for_model(models.VisualCondition)
    reference_ct = ContentType.objects.get_for_model(models.VisualReference)
    region_ct = ContentType.objects.get_for_model(models.VisualRegion)

    condition_pks = models.VisualCondition.objects.filter(visual=visual).values_list(
        'pk', flat=True
    )
    reference_pks = models.VisualReference.objects.filter(visual=visual).values_list(
        'pk', flat=True
    )
    region_pks = models.VisualRegion.objects.filter(visual=visual).values_list('pk', flat=True)

    return (
        Activity.objects.prefetch_user()
        .filter(
            Q(content_type=ContentType.objects.get_for_model(models.Visual), object_id=visual.pk)
            | Q(content_type=condition_ct, object_id__in=condition_pks)
            | Q(content_type=reference_ct, object_id__in=reference_pks)
            | Q(content_type=region_ct, object_id__in=region_pks)
        )
        .order_by('-created_datetime')[:10]
    )


@permission_required('django_spire_metric_visual.view_visual')
def detail_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    visual = get_object_or_404(
        models.Visual.objects.with_statistic().prefetch_related(
            Prefetch('conditions', queryset=models.VisualCondition.objects.not_deleted()),
            Prefetch('references', queryset=models.VisualReference.objects.not_deleted()),
        ),
        pk=pk,
    )

    nav = VisualNavigation()
    nav.breadcrumbs.add(
        name=str(visual), view_name='django_spire:metric:visual:page:detail', view_kwargs={'pk': pk}
    )

    value_date = _browse_value_date(request)

    context = nav.as_context()
    context.update(_visual_context(request, visual, value_date))
    context['value_date'] = value_date
    context['today'] = timezone.localdate()
    context['activity_log'] = _visual_activity_log(visual)

    return TemplateResponse(
        request, context=context, template='django_spire/metric/visual/page/detail_page.html'
    )


@permission_required('django_spire_metric_visual.view_visual')
def list_view(request: WSGIRequest) -> TemplateResponse:
    visuals = models.Visual.objects.with_statistic().not_deleted()

    Glue.queryset(request, 'visuals', visuals, Glue.Access.CHANGE, fields='__all__')

    nav = VisualNavigation()

    context = nav.as_context()

    return TemplateResponse(
        request, context=context, template='django_spire/metric/visual/page/list_page.html'
    )
