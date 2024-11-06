from __future__ import annotations

from typing_extensions import TYPE_CHECKING

from django.shortcuts import get_object_or_404

from django_spire.views import portal_views

from examples.form import models

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest
    from django.template.response import TemplateResponse


def form_detail_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    form = get_object_or_404(models.Form, pk=pk)

    context_data = {
        'form': form,
    }

    return portal_views.detail_view(
        request,
        obj=form,
        context_data=context_data,
        template='form/page/form_detail_page.html'
    )
