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

from django_spire.metric.visual.presentation import forms, models
from django_spire.metric.visual.presentation.navigation import PresentationNavigation

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


@permission_required('visual_presentation.delete_presentation')
def delete_modal_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    presentation = get_object_or_404(models.Presentation, pk=pk)

    form_action = reverse('metric:visual:presentation:form:delete_modal', kwargs={'pk': pk})
    fallback = reverse('metric:visual:presentation:page:list')
    return_url = safe_redirect_url(request, fallback=fallback)

    if request.method == 'POST':
        form = DeleteConfirmationForm(data=request.POST, obj=presentation)

        if form.is_valid():
            if form.cleaned_data['should_delete']:
                presentation.add_activity(
                    user=request.user,
                    verb='deleted',
                    information=f'{request.user.get_full_name()} deleted a presentation.',
                )
                presentation.set_deleted()

            return HttpResponseRedirect(return_url)
    else:
        form = DeleteConfirmationForm(obj=presentation)

    nav = PresentationNavigation()
    nav.page_title = 'Delete Presentation'
    context = nav.as_context()
    context['form'] = form
    context['form_title'] = 'Delete Presentation'
    context['form_description'] = (
        f'Are you sure you would like to delete presentation "{presentation}"?'
    )
    context['form_action'] = form_action
    return TemplateResponse(
        request,
        context=context,
        template='django_spire/contrib/page/delete_confirmation_form_page.html',
    )


@permission_required('visual_presentation.delete_presentation')
def delete_form_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    presentation = get_object_or_404(models.Presentation, pk=pk)
    return_url = request.GET.get('return_url', reverse('metric:visual:presentation:page:list'))

    if request.method == 'POST':
        form = DeleteConfirmationForm(data=request.POST, obj=presentation)

        if form.is_valid():
            if form.cleaned_data['should_delete']:
                presentation.set_deleted()
                presentation.add_activity(
                    user=request.user,
                    verb='deleted',
                    information=(
                        f'{request.user.get_full_name()} deleted presentation "{presentation}".'
                    ),
                )

            return HttpResponseRedirect(return_url)
    else:
        form = DeleteConfirmationForm(obj=presentation)

    nav = PresentationNavigation()
    nav.page_title = 'Delete Presentation'
    nav.breadcrumbs.add('Presentations', reverse('metric:visual:presentation:page:list'))
    nav.breadcrumbs.add(str(presentation))
    nav.breadcrumbs.add('Delete')
    context = nav.as_context()
    context['form'] = form
    context['form_title'] = f'Delete {presentation}'
    context['form_description'] = (
        f'Are you sure you would like to delete presentation "{presentation}"?'
    )
    return TemplateResponse(
        request,
        context=context,
        template='django_spire/contrib/page/delete_confirmation_form_page.html',
    )


@permission_required('visual_presentation.add_presentation')
def create_modal_view(request: WSGIRequest) -> TemplateResponse:
    return _modal_view(request)


@permission_required('visual_presentation.change_presentation')
def update_modal_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    return _modal_view(request, pk)


def _modal_view(request: WSGIRequest, pk: int = 0) -> TemplateResponse:
    presentation = get_object_or_404(models.Presentation, pk=pk)

    Glue.model(request, 'presentation', presentation)

    context_data = {'presentation': presentation}

    return TemplateResponse(
        request, context=context_data, template='metric/visual/presentation/modal/content/form.html'
    )


@permission_required('visual_presentation.add_presentation')
def create_view(request: WSGIRequest) -> TemplateResponse:
    return _form_view(request)


@permission_required('visual_presentation.change_presentation')
def update_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    return _form_view(request, pk)


def _form_view(request: WSGIRequest, pk: int = 0) -> TemplateResponse | HttpResponseRedirect:
    presentation = get_object_or_null_obj(models.Presentation, pk=pk)

    Glue.model(request, 'presentation', presentation, 'view')

    if request.method == 'POST':
        form = forms.PresentationForm(request.POST, instance=presentation)

        if form.is_valid():
            presentation, _ = presentation.services.save_model_obj(**form.cleaned_data)
            add_form_activity(presentation, pk, request.user)

            return redirect(
                request.GET.get('return_url', reverse('metric:visual:presentation:page:list'))
            )

        show_form_errors(request, form)
    else:
        form = forms.PresentationForm(instance=presentation)

    nav = PresentationNavigation()
    nav.page_title = str(presentation._meta.verbose_name.title())
    nav.page_description = 'Edit' if presentation.pk else 'Create'
    nav.breadcrumbs.add('Presentations', reverse('metric:visual:presentation:page:list'))
    nav.breadcrumbs.add('Edit' if presentation.pk else 'Create')
    context = nav.as_context()
    context['form'] = form
    return TemplateResponse(request, 'metric/visual/presentation/page/form_page.html', context)
