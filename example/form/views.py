from __future__ import annotations

from typing_extensions import TYPE_CHECKING

from django.shortcuts import get_object_or_404

from django_spire.views import portal_views

from example.form import models

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest
    from django.template.response import TemplateResponse


def form_detail_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    form = get_object_or_404(models.FormExample, pk=pk)

    context_data = {
        'form': form,
    }

    return portal_views.detail_view(
        request,
        obj=form,
        context_data=context_data,
        template='form/page/form_detail_page.html'
    )


def form_list_view(request: WSGIRequest) -> TemplateResponse:
    context_data = {
        'forms': models.FormExample.objects.all()
    }

    return portal_views.list_view(
        request,
        model=models.FormExample,
        context_data=context_data,
        template='form/page/form_list_page.html'
    )
