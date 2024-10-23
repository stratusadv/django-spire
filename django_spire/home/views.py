from django.conf import settings
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import reverse

from django_spire.core.views import portal_views
from django_spire.core.breadcrumbs import Breadcrumbs


def home_view(request):
    crumbs = Breadcrumbs()
    crumbs.add_breadcrumb(name='Home', href=reverse('home:home'))
    return portal_views.template_view(
        request,
        page_title='Home',
        page_description='Your Portal',
        breadcrumbs=crumbs,
        template='home/page/home_page.html'
    )


def maintenance_mode_view(request):
    if not settings.MAINTENANCE_MODE:
        return HttpResponseRedirect(request.GET.get('next', reverse('home:home')))
    else:
        return TemplateResponse(request, template='home/page/maintenance_mode_page.html')
