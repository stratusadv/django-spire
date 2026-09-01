from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib.auth.decorators import permission_required
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django_glue import Glue

from django_spire.metric.visual.presentation import models
from django_spire.metric.visual.presentation.constants import SLIDE_GRID_COLUMNS
from django_spire.metric.visual.presentation.navigation import PresentationNavigation
from django_spire.metric.visual.presentation.services.transformation_service import (
    SlideSectionTransformationService,
)

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


def _slide_data(request: WSGIRequest, slide: models.Slide) -> dict:
    sections = []
    section_sections = slide.sections.all()
    grid_styles = SlideSectionTransformationService.section_grid_styles(section_sections)

    for section in section_sections:
        section_data = {
            'section': section,
            'grid_style': grid_styles[section.pk],
            **section.services.transformation.render_context(),
        }

        chart = section_data.get('chart')
        if chart is not None:
            chart.glue(request)

        sections.append(section_data)

    return {'slide': slide, 'sections': sections, 'grid_columns': SLIDE_GRID_COLUMNS}


@permission_required('django_spire_metric_visual_presentation.view_presentation')
def detail_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    presentation = get_object_or_404(
        models.Presentation.objects.with_slides().with_slide_count(), pk=pk
    )

    nav = PresentationNavigation()
    nav.page_title = str(presentation)
    nav.breadcrumbs.add('Presentations', 'django_spire:metric:visual:presentation:page:list')
    nav.breadcrumbs.add(str(presentation))
    context = nav.as_context()
    context['presentation'] = presentation
    context['slides'] = [_slide_data(request, slide) for slide in presentation.slides.all()]

    return TemplateResponse(
        request,
        context=context,
        template='django_spire/metric/visual/presentation/page/detail_page.html',
    )


@permission_required('django_spire_metric_visual_presentation.view_presentation')
def list_view(request: WSGIRequest) -> TemplateResponse:
    presentations = models.Presentation.objects.with_slide_count()

    Glue.queryset(request, 'presentations', presentations, Glue.Access.CHANGE, fields='__all__')

    nav = PresentationNavigation()
    nav.page_title = 'Presentations'
    nav.breadcrumbs.add('Presentations')
    context = nav.as_context()
    context['presentations'] = presentations
    context['presentation_count'] = presentations.count()

    return TemplateResponse(
        request,
        context=context,
        template='django_spire/metric/visual/presentation/page/list_page.html',
    )
