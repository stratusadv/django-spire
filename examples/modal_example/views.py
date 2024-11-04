from __future__ import annotations

from django.http import HttpResponse
from django.template.response import TemplateResponse


def modal_page_one(request):
    return HttpResponse('<h2>Modal Page One Content</h2>')


def modal_page_two(request):
    return HttpResponse('<h2>Modal Page Two Content</h2>')


def modal_page_three(request):
    return HttpResponse('<h2>Modal Page Three Content</h2>')


def modal_form_submit(request):
    if request.method == 'POST':
        return HttpResponse('Form submitted successfully.')

    return HttpResponse('Invalid request.')


def modal_page_view(request):
    return TemplateResponse(
        request,
        template='page/modal.html'
    )
