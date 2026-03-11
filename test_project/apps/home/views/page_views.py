from __future__ import annotations

from typing import TYPE_CHECKING

from django.template.response import TemplateResponse
from django.urls import reverse

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


def home_view(request: WSGIRequest) -> TemplateResponse:
    return TemplateResponse(
        request,
        template='home/page/home_page.html',
    )

