from __future__ import annotations

from typing_extensions import TYPE_CHECKING

from django.shortcuts import get_object_or_404

from django_spire.views import portal_views

from example.maintenance import models

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest
    from django.template.response import TemplateResponse


def maintenance_detail_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    maintenance = get_object_or_404(models.MaintenanceExample, pk=pk)

    context_data = {
        'maintenance': maintenance,
    }

    return portal_views.detail_view(
        request,
        obj=maintenance,
        context_data=context_data,
        template='maintenance/page/maintenance_detail_page.html'
    )
