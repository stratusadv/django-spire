from django.template.response import TemplateResponse
from playground.utils import generate_test_model


def home_page_view(request):
    return TemplateResponse(
        request,
        template='page/home.html'
    )


def test_model_view(request):
    model = generate_test_model()

    return TemplateResponse(
        request,
        context_data={'model': model},
        template='page/home.html'
    )
