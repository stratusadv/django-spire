from __future__ import annotations

from django.template.response import TemplateResponse
from typing_extensions import TYPE_CHECKING

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


def chat_home_view(request: WSGIRequest) -> TemplateResponse:
    template = 'ai/chat/page/chat_home_page.html'

    return TemplateResponse(request, template, context={})
