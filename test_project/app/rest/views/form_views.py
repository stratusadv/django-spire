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


def create_view(request: WSGIRequest) -> TemplateResponse | redirect:
    pirate = models.Pirate()
    return _form_view(request, pirate)


def update_view(request: WSGIRequest, pk: int) -> TemplateResponse | redirect:
    pirate = get_object_or_404(models.Pirate, pk=pk)
    return _form_view(request, pirate)


def _form_view(request: WSGIRequest, pirate: models.Pirate) -> TemplateResponse | redirect:
    if request.method == 'POST':
        form = forms.PirateModelForm(request.POST, instance=pirate)
        if form.is_valid():
            pirate.services.save_model_obj(user=request.user, **form.cleaned_data)
            return redirect(request.GET.get('return_url', reverse('rest:page:list')))
    else:
        form = forms.PirateModelForm(instance=pirate)

    nav = RestNavigation()
    nav.set_page_title_from_model_instance_form_action(pirate)
    nav.breadcrumbs.add(str(pirate) if pirate.pk else 'New Pirate')

    context = nav.as_context()
    context['form'] = form

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
    form = forms.PirateGlueModelForm(request.POST or None, instance=pirate)

    Glue.form(request, 'pirate_model_form', form, Glue.Access.DELETE)

    nav = RestNavigation()
    nav.set_page_title_from_model_instance_form_action(pirate)
    nav.breadcrumbs.add(str(pirate) if pirate.pk else 'New Pirate (Glue)')

    context = {**nav.as_context()}

    return TemplateResponse(
        request=request, context=context, template='rest/page/glue_form_page.html'
    )
