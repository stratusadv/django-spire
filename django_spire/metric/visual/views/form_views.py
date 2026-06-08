from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib.auth.decorators import permission_required
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.urls import reverse

from django_spire.contrib.form.confirmation_forms import DeleteConfirmationForm
from django_spire.contrib.form.tools import show_form_errors

from django_spire.contrib.redirects import safe_redirect_url
from django_spire.contrib.shortcuts import get_object_or_null_obj
from django_spire.history.activity.utils import add_form_activity

from django_glue import Glue

from django_spire.metric.visual import forms, models

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


@permission_required('metric_visual.delete_visual')
def delete_form_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    visual = get_object_or_404(models.Visual, pk=pk)
    return_url = request.GET.get('return_url', reverse('metric:visual:page:list'))

    if request.method == 'POST':
        form = DeleteConfirmationForm(data=request.POST, obj=visual)

        if form.is_valid():
            if form.cleaned_data['should_delete']:
                visual.set_deleted()
                visual.add_activity(
                    user=request.user,
                    verb='deleted',
                    information=f'{request.user.get_full_name()} deleted visual "{visual}".',
                )

            return HttpResponseRedirect(return_url)
    else:
        form = DeleteConfirmationForm(obj=visual)

    return TemplateResponse(
        request,
        context={
            'request': request,
            'form': form,
            'form_title': f'Delete {visual}',
            'form_description': f'Are you sure you would like to delete visual "{visual}"?',
            'django_spire_navigation': {
                'page_title': 'Delete Visual',
                'breadcrumbs': [
                    {'name': 'Visuals', 'href': reverse('metric:visual:page:list')},
                    {'name': str(visual), 'href': None},
                    {'name': 'Delete', 'href': None},
                ],
            },
        },
        template='django_spire/page/delete_confirmation_form_page.html',
    )


@permission_required('metric_visual.delete_visual')
def delete_modal_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    visual = get_object_or_404(models.Visual, pk=pk)

    form_action = reverse('metric:visual:form:delete_modal', kwargs={'pk': pk})
    fallback = reverse('metric:visual:page:list')
    return_url = safe_redirect_url(request, fallback=fallback)

    if request.method == 'POST':
        form = DeleteConfirmationForm(data=request.POST, obj=visual)

        if form.is_valid():
            if form.cleaned_data['should_delete']:
                visual.add_activity(
                    user=request.user,
                    verb='deleted',
                    information=f'{request.user.get_full_name()} deleted a visual.',
                )
                visual.set_deleted()

            return HttpResponseRedirect(return_url)
    else:
        form = DeleteConfirmationForm(obj=visual)

    return TemplateResponse(
        request,
        context={
            'request': request,
            'form': form,
            'form_title': 'Delete Visual',
            'form_description': f'Are you sure you would like to delete visual "{visual}"?',
            'form_action': form_action,
            'django_spire_navigation': {'page_title': 'Delete Visual'},
        },
        template='django_spire/page/delete_confirmation_form_page.html',
    )


@permission_required('metric_visual.add_visual')
def create_modal_view(request: WSGIRequest) -> TemplateResponse:
    return _modal_view(request)


@permission_required('metric_visual.change_visual')
def update_modal_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    return _modal_view(request, pk)


def _modal_view(request: WSGIRequest, pk: int = 0) -> TemplateResponse:
    visual = get_object_or_404(models.Visual, pk=pk)

    Glue.model(request, 'visual', visual)

    context_data = {'request': request, 'visual': visual}

    return TemplateResponse(
        request, context=context_data, template='metric/visual/modal/content/form.html'
    )


@permission_required('metric_visual.add_visual')
def create_view(request: WSGIRequest) -> TemplateResponse:
    return _form_view(request)


@permission_required('metric_visual.change_visual')
def update_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    return _form_view(request, pk)


def _form_view(request: WSGIRequest, pk: int = 0) -> TemplateResponse | HttpResponseRedirect:
    visual = get_object_or_null_obj(models.Visual, pk=pk)

    Glue.model(request, 'visual', visual, 'view')

    if request.method == 'POST':
        form = forms.VisualForm(request.POST, instance=visual)

        if form.is_valid():
            visual, _ = visual.services.save_model_obj(**form.cleaned_data)
            add_form_activity(visual, pk, request.user)

            return redirect(request.GET.get('return_url', reverse('metric:visual:page:list')))

        show_form_errors(request, form)
    else:
        form = forms.VisualForm(instance=visual)

    context = {
        'form': form,
        'page_title': str(visual._meta.verbose_name.title()),
        'page_description': 'Edit' if visual.pk else 'Create',
        'breadcrumbs': [
            {'name': 'Visuals', 'href': reverse('metric:visual:page:list')},
            {'name': 'Edit' if visual.pk else 'Create', 'href': None},
        ],
    }
    return TemplateResponse(request, 'metric/visual/page/form_page.html', context)
