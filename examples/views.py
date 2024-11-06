from __future__ import annotations

from typing_extensions import TYPE_CHECKING

from django.contrib.auth.models import User
from django.template.response import TemplateResponse
from examples.context_data import get_app_context_data
from examples.utils import generate_test_model

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


def component_view(request: WSGIRequest) -> TemplateResponse:
    template = 'page/component.html'
    return TemplateResponse(request, template)


def modal_view(request: WSGIRequest) -> TemplateResponse:
    template = 'page/modal.html'
    return TemplateResponse(request, template)


def test_model_view(request: WSGIRequest) -> TemplateResponse:
    model = generate_test_model()

    user, created = User.objects.get_or_create(
        username="test_user",
        defaults={"password": "test_password"}
    )

    fields = {
        field.name: getattr(model, field.name)
        for field in model._meta.fields
    }

    model.add_activity(
        user=user,
        verb='created',
        information=f'{request.user} added a model.'
    )

    activities = model.activity_log.all()

    context = {
        'activities': activities,
        'fields': fields
    }

    return TemplateResponse(
        request,
        context=context,
        template='page/test_model.html'
    )
