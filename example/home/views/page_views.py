from __future__ import annotations

from django.template.response import TemplateResponse
from typing_extensions import TYPE_CHECKING

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


def home_view(request: WSGIRequest) -> TemplateResponse:
    return TemplateResponse(
        request,
        'home/page/home_page.html',
    )

