from __future__ import annotations

from django.template.response import TemplateResponse
from typing_extensions import TYPE_CHECKING

from test_project.apps.tabular.context_data import tabular_context_data

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


def tabular_home_view(request: WSGIRequest) -> TemplateResponse:
    context = tabular_context_data()

    template = 'tabular/page/tabular_home_page.html'
    return TemplateResponse(request, template, context=context)


