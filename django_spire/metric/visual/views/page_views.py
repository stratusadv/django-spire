from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib.auth.decorators import permission_required
from django.shortcuts import get_object_or_404
from django_glue import Glue

from django_spire.metric.visual import models
from django_spire.metric.visual.navigation import VisualNavigation

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest

from django.template.response import TemplateResponse


def _visual_context(request: WSGIRequest, visual: models.Visual) -> dict:
    context = {
        'visual': visual,
        'current_value': visual.services.transformation.current_value(),
        'current_condition': visual.services.transformation.current_condition(),
    }

    chart = visual.services.transformation.chart()
    if chart is not None:
        chart.glue(request)
        context['chart'] = chart

    return context


@permission_required('metric_visual.view_visual')
def detail_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    visual = get_object_or_404(models.Visual.objects.with_statistic().with_conditions(), pk=pk)

    nav = VisualNavigation()
    nav.page_title = str(visual)
    nav.breadcrumbs.add('Visuals', 'django_spire:metric:visual:page:list')
    nav.breadcrumbs.add(str(visual))
    context = nav.as_context()
    context.update(_visual_context(request, visual))
    context['period_start'], context['period_end'] = visual.services.transformation.date_range()

    return TemplateResponse(
        request, context=context, template='django_spire/metric/visual/page/detail_page.html'
    )


@permission_required('metric_visual.view_visual')
def list_view(request: WSGIRequest) -> TemplateResponse:
    visuals = models.Visual.objects.with_statistic()

    Glue.queryset(request, 'visuals', visuals, Glue.Access.CHANGE, fields='__all__')

    nav = VisualNavigation()
    nav.page_title = 'Visuals'
    nav.breadcrumbs.add('Visuals')
    context = nav.as_context()
    context['visuals'] = visuals
    context['visual_count'] = visuals.count()

    return TemplateResponse(
        request, context=context, template='django_spire/metric/visual/page/list_page.html'
    )
