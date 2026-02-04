from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib.auth.decorators import permission_required
from django.shortcuts import get_object_or_404
from django.urls import reverse

from django_spire.contrib.generic_views import portal_views
from django_spire.core.table.enums import ResponsiveMode
from django_spire.contrib.session.controller import SessionController


from django_spire.metric.domain import models
from django_spire.metric.domain.forms import DomainListFilterForm
from django_spire.metric.domain.constants import LIST_FILTERING_SESSION_KEY

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest
    from django.template.response import TemplateResponse


@permission_required('metric_domain.view_domain')
def detail_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    domain = get_object_or_404(models.Domain, pk=pk)

    context_data = {
        'domain': domain,
    }

    return portal_views.detail_view(
        request,
        obj=domain,
        context_data=context_data,
        template='metric/domain/page/detail_page.html'
    )


@permission_required('metric_domain.view_domain')
def list_view(request: WSGIRequest) -> TemplateResponse:
    models.Domain.objects.process_session_filter(
        request=request,
        session_key=LIST_FILTERING_SESSION_KEY,
        form_class=DomainListFilterForm,
    )

    context_data = {
        'responsive_mode': ResponsiveMode.SCROLL,
        'domain_items_endpoint': reverse('metric:domain:template:items'),
        'filter_session': SessionController(request, LIST_FILTERING_SESSION_KEY),
    }

    return portal_views.list_view(
        request,
        model=models.Domain,
        context_data=context_data,
        template='metric/domain/page/list_page.html'
    )
