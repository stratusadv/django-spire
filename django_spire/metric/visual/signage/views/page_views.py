from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib.auth.decorators import permission_required
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.urls import reverse

from django_spire.core.table.enums import ResponsiveMode
from django_spire.contrib.session.controller import SessionController


from django_spire.metric.visual.signage import models
from django_spire.metric.visual.signage.forms import SignageListFilterForm
from django_spire.metric.visual.signage.constants import LIST_FILTERING_SESSION_KEY
from django_spire.metric.visual.signage.navigation import SignageNavigation

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


@permission_required('visual_signage.view_signage')
def detail_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    signage = get_object_or_404(models.Signage, pk=pk)

    nav = SignageNavigation()
    nav.page_title = str(signage)
    nav.breadcrumbs.add('Signage', 'metric:visual:signage:page:list')
    nav.breadcrumbs.add(str(signage))
    context = nav.as_context()
    context['signage'] = signage

    return TemplateResponse(
        request, context=context, template='metric/visual/signage/page/detail_page.html'
    )


@permission_required('visual_signage.view_signage')
def list_view(request: WSGIRequest) -> TemplateResponse:
    models.Signage.objects.process_session_filter(
        request=request, session_key=LIST_FILTERING_SESSION_KEY, form_class=SignageListFilterForm
    )

    nav = SignageNavigation()
    nav.page_title = 'Signage'
    nav.breadcrumbs.add('Signage')
    context = nav.as_context()
    context['responsive_mode'] = ResponsiveMode.SCROLL
    context['signage_items_endpoint'] = reverse('metric:visual:signage:template:items')
    context['filter_session'] = SessionController(request, LIST_FILTERING_SESSION_KEY)

    return TemplateResponse(
        request, context=context, template='metric/visual/signage/page/list_page.html'
    )
