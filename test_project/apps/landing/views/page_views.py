from __future__ import annotations

from typing import TYPE_CHECKING

from django.template.response import TemplateResponse

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


def landing_page_view(request: WSGIRequest) -> TemplateResponse:
    return TemplateResponse(
        request,
        template='landing/page/landing_page.html'
    )
