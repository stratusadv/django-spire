from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib.auth.models import User
from django.template.response import TemplateResponse
from django.urls import reverse

from test_project.app.model_and_service.factories import generate_test_model

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


def test_model_detail_view(request: WSGIRequest) -> TemplateResponse:
    test_model = generate_test_model()

    user, _ = User.objects.get_or_create(
        username='test_user', defaults={'password': 'test_password'}
    )

    fields = {field.name: getattr(test_model, field.name) for field in test_model._meta.fields}

    test_model.add_activity(user=user, verb='created', information=f'{request.user} added a model.')

    context_data = {'adult': test_model, 'fields': fields}
    context_data['page_title'] = 'Test Model'
    context_data['page_description'] = 'Detail View'
    context_data['breadcrumbs'] = [
        {'name': 'Test Models', 'href': reverse('test_model:list')},
        {'name': 'Test Model', 'href': None},
    ]
    return TemplateResponse(
        request, context=context_data, template='model_and_service/page/adult_detail_page.html'
    )


def test_model_home_view(request: WSGIRequest) -> TemplateResponse:
    template = 'model_and_service/page/model_and_service_home_page.html'
    return TemplateResponse(request, template)


def test_model_list_view(request: WSGIRequest) -> TemplateResponse:
    context_data = {'adults': []}
    context_data['page_title'] = 'Test Model'
    context_data['page_description'] = 'List View'
    context_data['breadcrumbs'] = [{'name': 'Test Models', 'href': None}]

    return TemplateResponse(
        request, context=context_data, template='model_and_service/page/adult_list_page.html'
    )
