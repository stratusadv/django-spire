from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib.auth.decorators import permission_required
from django.shortcuts import get_object_or_404
from django.urls import reverse

from django_spire.contrib.generic_views import portal_views
from django_spire.core.table.enums import ResponsiveMode
from django_spire.contrib.session.controller import SessionController


from django_spire.metric.visual.presentation import models
from django_spire.metric.visual.presentation.forms import PresentationListFilterForm
from django_spire.metric.visual.presentation.constants import LIST_FILTERING_SESSION_KEY

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest
    from django.template.response import TemplateResponse


@permission_required('visual_presentation.view_presentation')
def detail_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    presentation = get_object_or_404(models.Presentation, pk=pk)

    context_data = {
        'presentation': presentation,
    }

    return portal_views.detail_view(
        request,
        obj=presentation,
        context_data=context_data,
        template='metric/visual/presentation/page/detail_page.html'
    )


@permission_required('visual_presentation.view_presentation')
def list_view(request: WSGIRequest) -> TemplateResponse:
    models.Presentation.objects.process_session_filter(
        request=request,
        session_key=LIST_FILTERING_SESSION_KEY,
        form_class=PresentationListFilterForm,
    )

    context_data = {
        'responsive_mode': ResponsiveMode.SCROLL,
        'presentation_items_endpoint': reverse('metric:visual:presentation:template:items'),
        'filter_session': SessionController(request, LIST_FILTERING_SESSION_KEY),
    }

    return portal_views.list_view(
        request,
        model=models.Presentation,
        context_data=context_data,
        template='metric/visual/presentation/page/list_page.html'
    )
