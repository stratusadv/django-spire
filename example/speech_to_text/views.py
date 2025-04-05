from __future__ import annotations

from django.template.response import TemplateResponse
from typing_extensions import TYPE_CHECKING

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


def ai_home_view(request: WSGIRequest) -> TemplateResponse:
    template = 'ai/page/ai_home_page.html'
    return TemplateResponse(request, template)
