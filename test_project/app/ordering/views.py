from __future__ import annotations

from typing import TYPE_CHECKING

from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.urls import reverse

from django_spire.contrib.form.confirmation_forms import DeleteConfirmationForm

from test_project.app.ordering import forms, models

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


def duck_list_view(request: WSGIRequest) -> TemplateResponse:
    ducks = models.Duck.objects.active().order_by('order')

    context = {
        'page_title': 'Duck',
        'page_description': 'List View',
        'breadcrumbs': [{'name': 'Ducks', 'href': None}],
        'ducks': ducks,
    }

    return TemplateResponse(request, context=context, template='ordering/page/duck_list_page.html')


def duck_detail_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    duck = get_object_or_404(models.Duck, pk=pk)

    context = {
        'page_title': str(duck),
        'page_description': 'Detail View',
        'breadcrumbs': [
            {'name': 'Ducks', 'href': reverse('order:list')},
            {'name': str(duck), 'href': None},
        ],
        'duck': duck,
    }

    return TemplateResponse(
        request, context=context, template='ordering/page/duck_detail_page.html'
    )


def duck_create_view(request: WSGIRequest) -> HttpResponseRedirect | TemplateResponse:
    if request.method == 'POST':
        form = forms.DuckForm(request.POST)

        if form.is_valid():
            duck = models.Duck()
            duck.services.save_model_obj(**form.cleaned_data)

            all_ducks = models.Duck.objects.active().order_by('order')
            duck.ordering_services.processor.move_to_position(
                destination_objects=all_ducks, position=duck.order
            )

            return redirect(reverse('order:list'))

        context = {'form': form}
    else:
        form = forms.DuckForm()
        context = {'form': form}

    context['page_title'] = 'Duck'
    context['page_description'] = 'Create'
    context['breadcrumbs'] = [
        {'name': 'Ducks', 'href': reverse('order:list')},
        {'name': 'Create', 'href': None},
    ]

    return TemplateResponse(request, context=context, template='ordering/page/duck_form_page.html')


def duck_update_view(request: WSGIRequest, pk: int) -> HttpResponseRedirect | TemplateResponse:
    duck = get_object_or_404(models.Duck, pk=pk)

    if request.method == 'POST':
        form = forms.DuckForm(request.POST, instance=duck)

        if form.is_valid():
            duck.services.save_model_obj(**form.cleaned_data)
            return redirect(reverse('order:list'))

        context = {'form': form, 'duck': duck}
    else:
        form = forms.DuckForm(instance=duck)
        context = {'form': form, 'duck': duck}

    context['page_title'] = str(duck)
    context['page_description'] = 'Edit'
    context['breadcrumbs'] = [
        {'name': 'Ducks', 'href': reverse('order:list')},
        {'name': str(duck), 'href': None},
    ]

    return TemplateResponse(request, context=context, template='ordering/page/duck_form_page.html')


def duck_delete_view(request: WSGIRequest, pk: int) -> HttpResponseRedirect | TemplateResponse:
    duck = get_object_or_404(models.Duck, pk=pk)
    return_url = reverse('order:list')

    if request.method == 'POST':
        form = DeleteConfirmationForm(data=request.POST, obj=duck)

        if form.is_valid():
            if form.cleaned_data['should_delete']:
                duck.ordering_services.processor.remove_from_objects(models.Duck.objects.active())
                duck.set_inactive()

            return HttpResponseRedirect(return_url)
    else:
        form = DeleteConfirmationForm(obj=duck)

    context = {
        'form': form,
        'form_title': f'Delete {duck}',
        'form_description': f'Are you sure you would like to delete duck "{duck}"?',
        'page_title': 'Delete Duck',
        'breadcrumbs': [
            {'name': 'Ducks', 'href': reverse('order:list')},
            {'name': str(duck), 'href': None},
            {'name': 'Delete', 'href': None},
        ],
    }

    return TemplateResponse(
        request, template='django_spire/page/delete_confirmation_form_page.html', context=context
    )


def reorder_view(_request: WSGIRequest, pk: int, order: int) -> JsonResponse:
    duck = models.Duck.objects.filter(pk=pk).first()

    if duck is None:
        return JsonResponse({'type': 'error', 'message': 'Duck not found'})

    all_ducks = models.Duck.objects.active().exclude(pk=pk).order_by('order')

    duck.ordering_services.processor.move_to_position(
        destination_objects=all_ducks, position=order, origin_objects=all_ducks
    )

    return JsonResponse({'type': 'success', 'message': 'Order updated successfully'})
