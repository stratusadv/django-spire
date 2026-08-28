from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib.auth.decorators import permission_required
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django_glue import Glue

from django_spire.metric.visual.presentation.constants import SLIDE_GRID_COLUMNS
from django_spire.metric.visual.signage import models
from django_spire.metric.visual.signage.navigation import SignageNavigation

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


@permission_required('django_spire_metric_visual_signage.view_signage')
def detail_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    signage = get_object_or_404(models.Signage, pk=pk)

    nav = SignageNavigation()
    nav.page_title = str(signage)
    nav.breadcrumbs.add('Signages', 'django_spire:metric:visual:signage:page:list')
    nav.breadcrumbs.add(str(signage))

    context = nav.as_context()
    context['signage'] = signage
    context['presentation_links'] = signage.services.transformation.presentation_links()

    return TemplateResponse(
        request,
        context=context,
        template='django_spire/metric/visual/signage/page/detail_page.html',
    )


@permission_required('django_spire_metric_visual_signage.view_signage')
def list_view(request: WSGIRequest) -> TemplateResponse:
    signages = models.Signage.objects.all()

    Glue.queryset(request, 'signages', signages, Glue.Access.CHANGE, fields='__all__')

    nav = SignageNavigation()
    nav.page_title = 'Signages'
    nav.breadcrumbs.add('Signages')
    context = nav.as_context()
    context['signages'] = signages
    context['signage_count'] = signages.count()

    return TemplateResponse(
        request, context=context, template='django_spire/metric/visual/signage/page/list_page.html'
    )


def display_view(request: WSGIRequest, key: str) -> TemplateResponse:
    signage = get_object_or_404(models.Signage.objects.for_key(key), key=key)

    nav = SignageNavigation()
    nav.page_title = str(signage)

    slides = signage.services.transformation.display_slides()

    for slide in slides:
        for section in slide['sections']:
            chart = section.get('chart')
            if chart is not None:
                chart.glue(request)

    context = {
        'signage': signage,
        'slides': slides,
        'slide_count': len(slides),
        'slide_timer_seconds': signage.slide_display_seconds,
        'grid_columns': SLIDE_GRID_COLUMNS,
        'chart_update_interval': 15,
        **nav.as_context(),
    }

    return TemplateResponse(
        request,
        context=context,
        template='django_spire/metric/visual/signage/page/display_page.html',
    )
