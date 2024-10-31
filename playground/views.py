from django.contrib.auth.models import User
from django.template.response import TemplateResponse
from playground.utils import generate_test_model


def home_page_view(request):
    return TemplateResponse(
        request,
        template='page/home.html'
    )


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
