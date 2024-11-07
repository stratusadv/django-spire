from __future__ import annotations

from typing_extensions import TYPE_CHECKING

from django.shortcuts import get_object_or_404

from django_spire.views import portal_views

from example.permission import models

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest
    from django.template.response import TemplateResponse


def permission_detail_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    permission = get_object_or_404(models.PermissionExample, pk=pk)

    context_data = {
        'permission': permission,
    }

    return portal_views.detail_view(
        request,
        obj=permission,
        context_data=context_data,
        template='permission/page/permission_detail_page.html'
    )
