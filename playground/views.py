from django.template.response import TemplateResponse
from playground.utils import generate_test_model


def home_page_view(request):
    return TemplateResponse(
        request,
        template='page/home.html'
    )


def test_model_view(request):
    model = generate_test_model()

    fields = {
        field.name: getattr(model, field.name)
        for field in model._meta.fields
    }

    return TemplateResponse(
        request,
        context={'fields': fields},
        template='page/test_model.html'
    )
