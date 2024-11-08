from __future__ import annotations

from typing_extensions import TYPE_CHECKING

from django.http import HttpResponse
from django.template.response import TemplateResponse

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


def modal_home_view(request: WSGIRequest) -> TemplateResponse:
    template = 'modal/page/modal_home_page.html'
    return TemplateResponse(request, template)


def modal_detail_view(request: WSGIRequest) -> TemplateResponse:
    template = 'modal/page/modal_detail_page.html'
    return TemplateResponse(request, template)


def modal_page_one(_: WSGIRequest) -> HttpResponse:
    return HttpResponse('<h2>Modal Page One Content</h2>')


def modal_page_two(_: WSGIRequest) -> HttpResponse:
    return HttpResponse('<h2>Modal Page Two Content</h2>')


def modal_page_three(_: WSGIRequest) -> HttpResponse:
    return HttpResponse('<h2>Modal Page Three Content</h2>')


def modal_form_submit(request: WSGIRequest) -> HttpResponse:
    if request.method == 'POST':
        return HttpResponse('Form submitted successfully.')

    return HttpResponse('Invalid request.')
