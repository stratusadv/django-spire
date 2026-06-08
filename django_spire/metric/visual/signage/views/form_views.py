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

from django_spire.metric.visual.signage import forms, models
from django_spire.metric.visual.signage.navigation import SignageNavigation

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


@permission_required('visual_signage.delete_signage')
def delete_modal_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    signage = get_object_or_404(models.Signage, pk=pk)

    form_action = reverse('metric:visual:signage:form:delete_modal', kwargs={'pk': pk})
    fallback = reverse('metric:visual:signage:page:list')
    return_url = safe_redirect_url(request, fallback=fallback)

    if request.method == 'POST':
        form = DeleteConfirmationForm(data=request.POST, obj=signage)

        if form.is_valid():
            if form.cleaned_data['should_delete']:
                signage.add_activity(
                    user=request.user,
                    verb='deleted',
                    information=f'{request.user.get_full_name()} deleted a signage.',
                )
                signage.set_deleted()

            return HttpResponseRedirect(return_url)
    else:
        form = DeleteConfirmationForm(obj=signage)

    nav = SignageNavigation()
    nav.page_title = 'Delete Signage'
    context = nav.as_context()
    context['form'] = form
    context['form_title'] = 'Delete Signage'
    context['form_description'] = f'Are you sure you would like to delete signage "{signage}"?'
    context['form_action'] = form_action

    return TemplateResponse(
        request, 'django_spire/page/delete_confirmation_form_page.html', context
    )


@permission_required('visual_signage.delete_signage')
def delete_form_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    signage = get_object_or_404(models.Signage, pk=pk)
    return_url = request.GET.get('return_url', reverse('metric:visual:signage:page:list'))

    if request.method == 'POST':
        form = DeleteConfirmationForm(data=request.POST, obj=signage)

        if form.is_valid():
            if form.cleaned_data['should_delete']:
                signage.set_deleted()
                signage.add_activity(
                    user=request.user,
                    verb='deleted',
                    information=f'{request.user.get_full_name()} deleted signage "{signage}".',
                )

            return HttpResponseRedirect(return_url)
    else:
        form = DeleteConfirmationForm(obj=signage)

    nav = SignageNavigation()
    nav.page_title = 'Delete Signage'
    nav.breadcrumbs.add_breadcrumb('Signage', reverse('metric:visual:signage:page:list'))
    nav.breadcrumbs.add_breadcrumb(str(signage), None)
    nav.breadcrumbs.add_breadcrumb('Delete', None)
    context = nav.as_context()
    context['form'] = form
    context['form_title'] = f'Delete {signage}'
    context['form_description'] = f'Are you sure you would like to delete signage "{signage}"?'

    return TemplateResponse(
        request, 'django_spire/page/delete_confirmation_form_page.html', context
    )


@permission_required('visual_signage.add_signage')
def create_modal_view(request: WSGIRequest) -> TemplateResponse:
    return _modal_view(request)


@permission_required('visual_signage.change_signage')
def update_modal_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    return _modal_view(request, pk)


def _modal_view(request: WSGIRequest, pk: int = 0) -> TemplateResponse:
    signage = get_object_or_404(models.Signage, pk=pk)

    Glue.model(request, 'signage', signage)

    context_data = {'signage': signage}

    return TemplateResponse(
        request, context=context_data, template='metric/visual/signage/modal/content/form.html'
    )


@permission_required('visual_signage.add_signage')
def create_view(request: WSGIRequest) -> TemplateResponse:
    return _form_view(request)


@permission_required('visual_signage.change_signage')
def update_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    return _form_view(request, pk)


def _form_view(request: WSGIRequest, pk: int = 0) -> TemplateResponse | HttpResponseRedirect:
    signage = get_object_or_null_obj(models.Signage, pk=pk)

    Glue.model(request, 'signage', signage, 'view')

    if request.method == 'POST':
        form = forms.SignageForm(request.POST, instance=signage)

        if form.is_valid():
            signage, _ = signage.services.save_model_obj(**form.cleaned_data)
            add_form_activity(signage, pk, request.user)

            return redirect(
                request.GET.get('return_url', reverse('metric:visual:signage:page:list'))
            )

        show_form_errors(request, form)
    else:
        form = forms.SignageForm(instance=signage)

    nav = SignageNavigation()
    nav.page_title = str(signage._meta.verbose_name.title())
    nav.breadcrumbs.add_breadcrumb('Signage', reverse('metric:visual:signage:page:list'))
    nav.breadcrumbs.add_breadcrumb('Edit' if signage.pk else 'Create', None)
    context = nav.as_context()
    context['form'] = form
    context['form_title'] = str(signage._meta.verbose_name.title())
    context['form_description'] = 'Edit' if signage.pk else 'Create'

    return TemplateResponse(request, 'metric/visual/signage/page/form_page.html', context)
