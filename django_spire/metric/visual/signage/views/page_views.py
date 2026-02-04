from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib.auth.decorators import permission_required
from django.shortcuts import get_object_or_404
from django.urls import reverse

from django_spire.contrib.generic_views import portal_views
from django_spire.core.table.enums import ResponsiveMode
from django_spire.contrib.session.controller import SessionController


from django_spire.metric.visual.signage import models
from django_spire.metric.visual.signage.forms import SignageListFilterForm
from django_spire.metric.visual.signage.constants import LIST_FILTERING_SESSION_KEY

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest
    from django.template.response import TemplateResponse


@permission_required('visual_signage.view_signage')
def detail_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    signage = get_object_or_404(models.Signage, pk=pk)

    context_data = {
        'signage': signage,
    }

    return portal_views.detail_view(
        request,
        obj=signage,
        context_data=context_data,
        template='metric/visual/signage/page/detail_page.html'
    )


@permission_required('visual_signage.view_signage')
def list_view(request: WSGIRequest) -> TemplateResponse:
    models.Signage.objects.process_session_filter(
        request=request,
        session_key=LIST_FILTERING_SESSION_KEY,
        form_class=SignageListFilterForm,
    )

    context_data = {
        'responsive_mode': ResponsiveMode.SCROLL,
        'signage_items_endpoint': reverse('metric:visual:signage:template:items'),
        'filter_session': SessionController(request, LIST_FILTERING_SESSION_KEY),
    }

    return portal_views.list_view(
        request,
        model=models.Signage,
        context_data=context_data,
        template='metric/visual/signage/page/list_page.html'
    )
