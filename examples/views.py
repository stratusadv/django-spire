from __future__ import annotations

from django.contrib.auth.models import User
from django.template.response import TemplateResponse
from examples.utils import generate_test_model


def home_page_view(request):
    return TemplateResponse(
        request,
        template='page/home.html'
    )


def component_view(request):
    template = 'page/component.html'
    return TemplateResponse(request, template)


def modal_view(request):
    template = 'page/modal.html'
    return TemplateResponse(request, template)


def test_model_view(request):
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
