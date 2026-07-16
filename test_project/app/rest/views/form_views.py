from __future__ import annotations

from typing import TYPE_CHECKING

from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.urls import reverse

from django_glue import Glue

from django_spire.contrib.redirects import safe_redirect_url
from django_spire.contrib.shortcuts import get_object_or_null_obj

from test_project.app.rest import forms, models
from test_project.app.rest.navigation import RestNavigation

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


def form_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    pirate = get_object_or_null_obj(models.Pirate, pk=pk)

    nav = RestNavigation()
    nav.set_page_title_to_form_action_from_model_instance(pirate)
    nav.breadcrumbs.add(str(pirate) if pirate.pk else 'New Pirate')

    form = forms.PirateModelForm(request.POST or None, instance=pirate)

    Glue.form(request, 'pirate_model_form', form, Glue.Access.DELETE)

    context = {**nav.as_context()}

    return TemplateResponse(request=request, context=context, template='rest/page/form_page.html')


def delete_view(request: WSGIRequest, pk: int) -> TemplateResponse | redirect:
    pirate = get_object_or_404(models.Pirate, pk=pk)
    return_url = safe_redirect_url(request, fallback=reverse('rest:page:list'))

    if request.method == 'POST':
        pirate.set_deleted()
        pirate.add_activity(
            user=request.user,
            verb='deleted',
            information=f'{request.user.get_full_name()} deleted pirate {pirate}.',
        )
        return redirect(return_url)

    nav = RestNavigation()
    nav.page_title = f'Delete {pirate}'
    nav.breadcrumbs.add('Pirates', 'rest:page:list')
    nav.breadcrumbs.add(f'Delete {pirate}')

    context = nav.as_context()
    context['pirate'] = pirate
    context['return_url'] = return_url

    return TemplateResponse(request=request, context=context, template='rest/page/delete_page.html')


def glue_form_view(request: WSGIRequest, pk: int) -> TemplateResponse | redirect:
    pirate = get_object_or_null_obj(models.Pirate, pk=pk)
    form = forms.PirateModelForm(request.POST or None, instance=pirate)

    Glue.form(request, 'pirate_model_form', form, Glue.Access.DELETE)

    nav = RestNavigation()
    nav.set_page_title_to_form_action_from_model_instance(pirate)
    nav.breadcrumbs.add(str(pirate) if pirate.pk else 'New Pirate (Glue)')

    context = {**nav.as_context()}

    return TemplateResponse(
        request=request, context=context, template='rest/page/glue_form_page.html'
    )
