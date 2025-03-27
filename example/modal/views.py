from __future__ import annotations

from typing_extensions import TYPE_CHECKING

from django.http import HttpResponse, HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import reverse

import django_glue as dg

from example.test_model.factories import generate_test_model

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


def modal_form_submit(request: WSGIRequest) -> HttpResponse:
    if request.method == 'POST':
        print(request.POST)
        return HttpResponseRedirect(reverse('modal:home'))

    return HttpResponse('Invalid request.', status=400)


def modal_home_view(request: WSGIRequest) -> TemplateResponse:
    test_model = generate_test_model()
    dg.glue_model_object(request, 'test_model', test_model)

    context = {'test_model': test_model}

    template = 'modal/page/modal_home_page.html'
    return TemplateResponse(request, template, context=context)


def modal_detail_view(request: WSGIRequest) -> TemplateResponse:
    template = 'modal/page/modal_detail_page.html'
    return TemplateResponse(request, template)


def modal_basic(request: WSGIRequest) -> HttpResponse:
    test_model = generate_test_model()
    dg.glue_model_object(request, 'test_model', test_model)

    context = {'test_model': test_model}

    template = 'modal/modal.html'
    return TemplateResponse(request, template, context=context)


def modal_page_one(request: WSGIRequest) -> HttpResponse:
    template = 'modal/content/page_one.html'
    return TemplateResponse(request, template)


def modal_page_two(request: WSGIRequest) -> HttpResponse:
    template = 'modal/content/page_two.html'
    return TemplateResponse(request, template)


def modal_page_three(request: WSGIRequest) -> HttpResponse:
    template = 'modal/content/page_three.html'
    return TemplateResponse(request, template)
