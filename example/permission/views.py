from __future__ import annotations

from typing_extensions import TYPE_CHECKING

from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse

from django_spire.contrib.generic_views import portal_views

from example.permission import models

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


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


def permission_home_view(request: WSGIRequest) -> TemplateResponse:
    template = 'permission/page/permission_home_page.html'
    return TemplateResponse(request, template)


def permission_list_view(request: WSGIRequest) -> TemplateResponse:
    context_data = {
        'permissions': models.PermissionExample.objects.all()
    }

    return portal_views.list_view(
        request,
        model=models.PermissionExample,
        context_data=context_data,
        template='permission/page/permission_list_page.html'
    )
