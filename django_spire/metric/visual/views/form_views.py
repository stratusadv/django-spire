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

from django_spire.metric.visual import forms, models

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest
    from django.http import HttpResponseRedirect


@permission_required('metric_visual.delete_visual')
def delete_modal_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    visual = get_object_or_404(models.Visual, pk=pk)

    form_action = reverse(
        'metric:visual:form:delete_modal',
        kwargs={'pk': pk}
    )

    def add_activity() -> None:
        visual.add_activity(
            user=request.user,
            verb='deleted',
            information=f'{request.user.get_full_name()} deleted a visual.'
        )

    fallback = reverse('metric:visual:page:list')
    return_url = safe_redirect_url(request, fallback=fallback)

    return modal_views.dispatch_modal_delete_form_content(
        request,
        obj=visual,
        form_action=form_action,
        activity_func=add_activity,
        return_url=return_url,
    )


@permission_required('metric_visual.delete_visual')
def delete_form_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    visual = get_object_or_404(models.Visual, pk=pk)

    return_url = request.GET.get(
        'return_url',
        reverse('metric:visual:page:list')
    )

    return portal_views.delete_form_view(
        request,
        obj=visual,
        return_url=return_url
    )


@permission_required('metric_visual.add_visual')
def create_modal_view(request: WSGIRequest) -> TemplateResponse:
    return _modal_view(request)


@permission_required('metric_visual.change_visual')
def update_modal_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    return _modal_view(request, pk)


def _modal_view(request: WSGIRequest, pk: int = 0) -> TemplateResponse:
    visual = get_object_or_404(models.Visual, pk=pk)

    dg.glue_model_object(request, 'visual', visual)

    context_data = {
        'visual': visual
    }

    return TemplateResponse(
        request,
        context=context_data,
        template='metric/visual/modal/content/form.html'
    )


@permission_required('metric_visual.add_visual')
def create_view(request: WSGIRequest) -> TemplateResponse:
    return _form_view(request)


@permission_required('metric_visual.change_visual')
def update_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    return _form_view(request, pk)


def _form_view(request: WSGIRequest, pk: int = 0) -> TemplateResponse|HttpResponseRedirect:
    visual = get_object_or_null_obj(models.Visual, pk=pk)

    dg.glue_model_object(request, 'visual', visual, 'view')

    if request.method == 'POST':
        form = forms.VisualForm(request.POST, instance=visual)

        if form.is_valid():
            visual, _ = visual.services.save_model_obj(**form.cleaned_data)
            add_form_activity(visual, pk, request.user)

            return redirect(
                request.GET.get(
                    'return_url',
                    reverse('metric:visual:page:list')
                )
            )

        show_form_errors(request, form)
    else:
        form = forms.VisualForm(instance=visual)

    return portal_views.form_view(
        request,
        form=form,
        obj=visual,
        template='metric/visual/page/form_page.html'
    )
