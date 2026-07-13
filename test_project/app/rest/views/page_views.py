from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse

from django_glue import Glue

from test_project.app.rest import models
from test_project.app.rest.navigation import RestNavigation

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


@login_required()
def list_page(request: WSGIRequest) -> TemplateResponse:
    pirates = models.Pirate.objects.active().search(request.GET.get('search'))

    Glue.model(request, 'pirate', models.Pirate())
    Glue.queryset(request, 'pirates', pirates, Glue.Access.CHANGE)

    nav = RestNavigation()
    nav.set_page_title_from_model_plural_name(models.Pirate)

    context = nav.as_context()

    return TemplateResponse(request=request, context=context, template='rest/page/list_page.html')


@login_required()
def detail_page(request: WSGIRequest, pk: int) -> TemplateResponse:
    pirate = get_object_or_404(models.Pirate, pk=pk)

    nav = RestNavigation()
    nav.page_title = str(pirate)
    nav.breadcrumbs.add_model_instance_string(pirate)

    context = nav.as_context()
    context['pirate'] = pirate

    return TemplateResponse(request=request, context=context, template='rest/page/detail_page.html')
