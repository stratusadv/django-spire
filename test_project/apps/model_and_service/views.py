from __future__ import annotations

from typing_extensions import TYPE_CHECKING

from test_project.apps.model_and_service.models import Adult

from django.contrib.auth.models import User
from django.template.response import TemplateResponse

from django_spire.contrib.generic_views import portal_views

from test_project.apps.model_and_service.factories import generate_test_model

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


def test_model_detail_view(request: WSGIRequest) -> TemplateResponse:
    test_model = generate_test_model()

    user, created = User.objects.get_or_create(
        username="test_user",
        defaults={"password": "test_password"}
    )

    fields = {
        field.name: getattr(test_model, field.name)
        for field in test_model._meta.fields
    }

    test_model.add_activity(
        user=user,
        verb='created',
        information=f'{request.user} added a model.'
    )


    context_data = {
        'fields': fields
    }

    return portal_views.detail_view(
        request,
        obj=test_model,
        context_data=context_data,
        template='test_model/page/test_model_detail_page.html'
    )


def test_model_home_view(request: WSGIRequest) -> TemplateResponse:
    template = 'test_model/page/test_model_home_page.html'
    return TemplateResponse(request, template)


def test_model_list_view(request: WSGIRequest) -> TemplateResponse:
    context_data = {
        'test_models': []
    }

    return portal_views.list_view(
        request,
        model=generate_test_model,
        context_data=context_data,
        template='test_model/page/test_model_list_page.html'
    )
