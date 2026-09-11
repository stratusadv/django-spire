from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib.auth.decorators import permission_required
from django.contrib.contenttypes.models import ContentType
from django.db.models import Prefetch, Q
from django.shortcuts import get_object_or_404
from django_glue import Glue

from django_spire.history.activity.models import Activity
from django_spire.metric.visual import models
from django_spire.metric.visual.navigation import VisualNavigation

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest

    from django.db.models import QuerySet

from django.template.response import TemplateResponse


def _visual_context(request: WSGIRequest, visual: models.Visual) -> dict:
    context = {
        'visual': visual,
        'current_value': visual.services.transformation.current_value(),
        'current_condition': visual.services.transformation.current_condition(),
        'period_start': visual.services.transformation.date_range()[0],
        'period_end': visual.services.transformation.date_range()[1],
    }

    chart = visual.services.transformation.chart()
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

    context = nav.as_context()
    context.update(_visual_context(request, visual))
    context['period_start'], context['period_end'] = visual.services.transformation.date_range()
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
