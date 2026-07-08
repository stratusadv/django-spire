from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib.auth.decorators import permission_required
from django.shortcuts import get_object_or_404
from django.urls import reverse

from django.template.response import TemplateResponse
from django_spire.core.table.enums import ResponsiveMode
from django_spire.contrib.session.controller import SessionController


from django_spire.metric.visual import models
from django_spire.metric.visual.forms import VisualListFilterForm
from django_spire.metric.visual.constants import LIST_FILTERING_SESSION_KEY
from django_spire.metric.visual.navigation import VisualNavigation

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest
else:
    from django.template.response import TemplateResponse


@permission_required('metric_visual.view_visual')
def detail_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    visual = get_object_or_404(models.Visual, pk=pk)

    nav = VisualNavigation()
    nav.page_title = str(visual)
    nav.breadcrumbs.add('Visuals', 'metric:visual:page:list')
    nav.breadcrumbs.add(str(visual))
    context = nav.as_context()
    context['visual'] = visual

    return TemplateResponse(
        request, context=context, template='metric/visual/page/detail_page.html'
    )


@permission_required('metric_visual.view_visual')
def list_view(request: WSGIRequest) -> TemplateResponse:
    models.Visual.objects.process_session_filter(
        request=request, session_key=LIST_FILTERING_SESSION_KEY, form_class=VisualListFilterForm
    )

    nav = VisualNavigation()
    nav.page_title = 'Visuals'
    nav.breadcrumbs.add('Visuals')
    context = nav.as_context()
    context['responsive_mode'] = ResponsiveMode.SCROLL
    context['visual_items_endpoint'] = reverse('metric:visual:template:items')
    context['filter_session'] = SessionController(request, LIST_FILTERING_SESSION_KEY)

    return TemplateResponse(request, context=context, template='metric/visual/page/list_page.html')
