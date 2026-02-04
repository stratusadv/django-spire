from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib.auth.decorators import permission_required
from django.shortcuts import get_object_or_404
from django.urls import reverse

from django_spire.contrib.generic_views import portal_views
from django_spire.core.table.enums import ResponsiveMode
from django_spire.contrib.session.controller import SessionController


from django_spire.metric.visual import models
from django_spire.metric.visual.forms import VisualListFilterForm
from django_spire.metric.visual.constants import LIST_FILTERING_SESSION_KEY

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest
    from django.template.response import TemplateResponse


@permission_required('metric_visual.view_visual')
def detail_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    visual = get_object_or_404(models.Visual, pk=pk)

    context_data = {
        'visual': visual,
    }

    return portal_views.detail_view(
        request,
        obj=visual,
        context_data=context_data,
        template='metric/visual/page/detail_page.html'
    )


@permission_required('metric_visual.view_visual')
def list_view(request: WSGIRequest) -> TemplateResponse:
    models.Visual.objects.process_session_filter(
        request=request,
        session_key=LIST_FILTERING_SESSION_KEY,
        form_class=VisualListFilterForm,
    )

    context_data = {
        'responsive_mode': ResponsiveMode.SCROLL,
        'visual_items_endpoint': reverse('metric:visual:template:items'),
        'filter_session': SessionController(request, LIST_FILTERING_SESSION_KEY),
    }

    return portal_views.list_view(
        request,
        model=models.Visual,
        context_data=context_data,
        template='metric/visual/page/list_page.html'
    )
