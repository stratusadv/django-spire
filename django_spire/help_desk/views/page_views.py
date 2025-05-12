from django.template.response import TemplateResponse

def list_view(request):
    return TemplateResponse(request, context = {}, template = 'django_spire/help_desk/page/list_page.html')
