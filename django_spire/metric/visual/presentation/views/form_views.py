from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib.auth.decorators import permission_required
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.urls import reverse

from django_spire.contrib.form.utils import show_form_errors
from django_spire.contrib.generic_views import modal_views, portal_views
from django_spire.core.redirect.safe_redirect import safe_redirect_url
from django_spire.core.shortcuts import get_object_or_null_obj
from django_spire.history.activity.utils import add_form_activity

import django_glue as dg

from django_spire.metric.visual.presentation import forms, models

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest
    from django.http import HttpResponseRedirect


@permission_required('visual_presentation.delete_presentation')
def delete_modal_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    presentation = get_object_or_404(models.Presentation, pk=pk)

    form_action = reverse(
        'metric:visual:presentation:form:delete_modal',
        kwargs={'pk': pk}
    )

    def add_activity() -> None:
        presentation.add_activity(
            user=request.user,
            verb='deleted',
            information=f'{request.user.get_full_name()} deleted a presentation.'
        )

    fallback = reverse('metric:visual:presentation:page:list')
    return_url = safe_redirect_url(request, fallback=fallback)

    return modal_views.dispatch_modal_delete_form_content(
        request,
        obj=presentation,
        form_action=form_action,
        activity_func=add_activity,
        return_url=return_url,
    )


@permission_required('visual_presentation.delete_presentation')
def delete_form_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    presentation = get_object_or_404(models.Presentation, pk=pk)

    return_url = request.GET.get(
        'return_url',
        reverse('metric:visual:presentation:page:list')
    )

    return portal_views.delete_form_view(
        request,
        obj=presentation,
        return_url=return_url
    )


@permission_required('visual_presentation.add_presentation')
def create_modal_view(request: WSGIRequest) -> TemplateResponse:
    return _modal_view(request)


@permission_required('visual_presentation.change_presentation')
def update_modal_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    return _modal_view(request, pk)


def _modal_view(request: WSGIRequest, pk: int = 0) -> TemplateResponse:
    presentation = get_object_or_404(models.Presentation, pk=pk)

    dg.glue_model_object(request, 'presentation', presentation)

    context_data = {
        'presentation': presentation
    }

    return TemplateResponse(
        request,
        context=context_data,
        template='metric/visual/presentation/modal/content/form.html'
    )


@permission_required('visual_presentation.add_presentation')
def create_view(request: WSGIRequest) -> TemplateResponse:
    return _form_view(request)


@permission_required('visual_presentation.change_presentation')
def update_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    return _form_view(request, pk)


def _form_view(request: WSGIRequest, pk: int = 0) -> TemplateResponse|HttpResponseRedirect:
    presentation = get_object_or_null_obj(models.Presentation, pk=pk)

    dg.glue_model_object(request, 'presentation', presentation, 'view')

    if request.method == 'POST':
        form = forms.PresentationForm(request.POST, instance=presentation)

        if form.is_valid():
            presentation, _ = presentation.services.save_model_obj(**form.cleaned_data)
            add_form_activity(presentation, pk, request.user)

            return redirect(
                request.GET.get(
                    'return_url',
                    reverse('metric:visual:presentation:page:list')
                )
            )

        show_form_errors(request, form)
    else:
        form = forms.PresentationForm(instance=presentation)

    return portal_views.form_view(
        request,
        form=form,
        obj=presentation,
        template='metric/visual/presentation/page/form_page.html'
    )
