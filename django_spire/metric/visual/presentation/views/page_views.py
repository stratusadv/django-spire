from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib.auth.decorators import permission_required
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.urls import reverse

from django_spire.contrib.session.controller import SessionController
from django_spire.core.table.enums import ResponsiveMode

from django_spire.metric.visual.presentation import models
from django_spire.metric.visual.presentation.constants import LIST_FILTERING_SESSION_KEY
from django_spire.metric.visual.presentation.forms import PresentationListFilterForm
from django_spire.metric.visual.presentation.navigation import PresentationNavigation

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


@permission_required('visual_presentation.view_presentation')
def detail_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    presentation = get_object_or_404(models.Presentation, pk=pk)

    nav = PresentationNavigation()
    nav.page_title = str(presentation)
    nav.page_description = 'Detail View'
    nav.breadcrumbs.add('Presentations', reverse('metric:visual:presentation:page:list'))
    nav.breadcrumbs.add(str(presentation))
    context = nav.as_context()
    context['presentation'] = presentation
    return TemplateResponse(
        request, context=context, template='metric/visual/presentation/page/detail_page.html'
    )


@permission_required('visual_presentation.view_presentation')
def list_view(request: WSGIRequest) -> TemplateResponse:
    models.Presentation.objects.process_session_filter(
        request=request,
        session_key=LIST_FILTERING_SESSION_KEY,
        form_class=PresentationListFilterForm,
    )

    nav = PresentationNavigation()
    nav.page_title = 'Presentation'
    nav.page_description = 'List View'
    nav.breadcrumbs.add('Presentations')
    context = nav.as_context()
    context['responsive_mode'] = ResponsiveMode.SCROLL
    context['presentation_items_endpoint'] = reverse('metric:visual:presentation:template:items')
    context['filter_session'] = SessionController(request, LIST_FILTERING_SESSION_KEY)
    return TemplateResponse(
        request, context=context, template='metric/visual/presentation/page/list_page.html'
    )
