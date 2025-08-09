from __future__ import annotations

from typing_extensions import TYPE_CHECKING

from django.contrib.auth.decorators import permission_required
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse

from django_spire.contrib.generic_views import portal_views

from module import forms, models


if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


@permission_required('spireparentapp.view_spirepermission')
def detail_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    spirechildapp = get_object_or_404(models.SpireChildApp, pk=pk)

    context_data = {
        'spirechildapp': spirechildapp,
    }

    return portal_views.detail_view(
        request,
        obj=spirechildapp,
        context_data=context_data,
        template='spirechildapp/page/detail_page.html'
    )


@permission_required('spireparentapp.view_spirepermission')
def list_view(request: WSGIRequest) -> TemplateResponse:
    context_data = {
        'spirechildapps': models.SpireChildApp.objects.all()
    }

    return portal_views.list_view(
        request,
        model=models.SpireChildApp,
        context_data=context_data,
        template='spirechildapp/page/list_page.html'
    )
