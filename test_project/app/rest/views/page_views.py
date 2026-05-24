from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib.auth.decorators import login_required
from django.template.response import TemplateResponse
from django.urls import reverse


if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


@login_required()
def list_page(request: WSGIRequest):
    context_data = {
        'endpoint': reverse('rest:template:list_items'),
    }

    return TemplateResponse(
        request=request,
        context=context_data,
        template='rest/page/list_page.html',
    )
