from __future__ import annotations

from typing_extensions import TYPE_CHECKING

from django.template.response import TemplateResponse
from example.context_data import get_app_context_data

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


def home_page_view(request: WSGIRequest) -> TemplateResponse:
    apps = get_app_context_data()
    context = {'apps': apps}

    return TemplateResponse(
        request,
        context=context,
        template='page/home.html'
    )
