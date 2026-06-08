from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib.auth.decorators import permission_required
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.urls import reverse

from django_spire.contrib.form.confirmation_forms import DeleteConfirmationForm
from django_spire.contrib.redirects import safe_redirect_url
from django_spire.contrib.shortcuts import get_object_or_null_obj
from django_spire.contrib.form.tools import show_form_errors
from django_glue import Glue


from test_project.app.ordering import forms, models

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


@permission_required('apps.change_appsordering')
def create_form_view(request: WSGIRequest) -> HttpResponseRedirect | TemplateResponse:
    duck = models.Duck()

    Glue.model(request, 'duck', duck, 'view')

    if request.method == 'POST':
        form = forms.DuckForm(request.POST, instance=duck)

        if form.is_valid():
            duck.services.save_model_obj(**form.cleaned_data)
            all_ducks = models.Duck.objects.active().order_by('order')
            duck.ordering_services.processor.move_to_position(
                destination_objects=all_ducks, position=duck.order
            )

            return redirect(request.GET.get('return_url', reverse('ordering:page:demo')))

        show_form_errors(request, form)
    else:
        form = forms.DuckForm(instance=duck)

    return TemplateResponse(
        request,
        context={
            'request': request,
            'form': form,
            'obj': duck,
            'page_title': 'Duck',
            'page_description': 'Create',
            'breadcrumbs': [{'name': 'Ducks', 'href': None}, {'name': 'Create', 'href': None}],
        },
        template='ordering/page/form_page.html',
    )


@permission_required('apps.delete_appsordering')
def delete_form_modal_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    duck = get_object_or_404(models.Duck, pk=pk)

    form_action = reverse('ordering:form:delete_form_modal', kwargs={'pk': pk})
    fallback = reverse('ordering:page:demo')
    return_url = safe_redirect_url(request, fallback=fallback)

    if request.method == 'POST':
        form = DeleteConfirmationForm(data=request.POST, obj=duck)

        if form.is_valid():
            if form.cleaned_data['should_delete']:
                duck.ordering_services.processor.remove_from_objects(models.Duck.objects.active())
                duck.set_inactive()

            return HttpResponseRedirect(return_url)
    else:
        form = DeleteConfirmationForm(obj=duck)

    return TemplateResponse(
        request,
        context={
            'form': form,
            'form_title': 'Delete Duck',
            'form_description': f'Are you sure you would like to delete duck "{duck}"?',
            'form_action': form_action,
            'django_spire_navigation': {'page_title': 'Delete Duck'},
        },
        template='django_spire/page/delete_confirmation_form_page.html',
    )


@permission_required('apps.change_appsordering')
def form_content_modal_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    duck = get_object_or_null_obj(models.Duck, pk=pk)
    action_url = reverse('ordering:form:form', kwargs={'pk': pk})
    unique_name = f'{duck.pk}_duck'

    if duck.id is None:
        duck = models.Duck()
        action_url = reverse('ordering:form:create')
        unique_name = 'duck'

    Glue.model(request, unique_name, duck)

    context_data = {'request': request, 'duck': duck, 'action_url': action_url, 'unique_name': unique_name}

    return TemplateResponse(
        request, context=context_data, template='ordering/modal/content/form_modal_content.html'
    )


@permission_required('apps.change_appsordering')
def form_view(request: WSGIRequest, pk: int) -> HttpResponseRedirect | TemplateResponse:
    duck = get_object_or_null_obj(models.Duck, pk=pk)

    Glue.model(request, 'duck', duck, 'view')

    if request.method == 'POST':
        form = forms.DuckForm(request.POST, instance=duck)

        if form.is_valid():
            duck.services.save_model_obj(**form.cleaned_data)

            return redirect(request.GET.get('return_url', reverse('ordering:page:demo')))

        show_form_errors(request, form)
    else:
        form = forms.DuckForm(instance=duck)

    return TemplateResponse(
        request,
        context={
            'request': request,
            'form': form,
            'obj': duck,
            'page_title': 'Duck',
            'page_description': 'Edit',
            'breadcrumbs': [{'name': 'Ducks', 'href': None}, {'name': str(duck), 'href': None}],
        },
        template='ordering/page/form_page.html',
    )
