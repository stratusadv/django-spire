from __future__ import annotations

from django.template.response import TemplateResponse
from typing_extensions import TYPE_CHECKING

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


def speech_to_text_home_view(request: WSGIRequest) -> TemplateResponse:
    template = 'speech_to_text/page/speech_to_text_home_page.html'
    return TemplateResponse(request, template)
