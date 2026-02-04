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

from django_spire.metric.visual.signage import forms, models

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest
    from django.http import HttpResponseRedirect


@permission_required('visual_signage.delete_signage')
def delete_modal_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    signage = get_object_or_404(models.Signage, pk=pk)

    form_action = reverse(
        'metric:visual:signage:form:delete_modal',
        kwargs={'pk': pk}
    )

    def add_activity() -> None:
        signage.add_activity(
            user=request.user,
            verb='deleted',
            information=f'{request.user.get_full_name()} deleted a signage.'
        )

    fallback = reverse('metric:visual:signage:page:list')
    return_url = safe_redirect_url(request, fallback=fallback)

    return modal_views.dispatch_modal_delete_form_content(
        request,
        obj=signage,
        form_action=form_action,
        activity_func=add_activity,
        return_url=return_url,
    )


@permission_required('visual_signage.delete_signage')
def delete_form_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    signage = get_object_or_404(models.Signage, pk=pk)

    return_url = request.GET.get(
        'return_url',
        reverse('metric:visual:signage:page:list')
    )

    return portal_views.delete_form_view(
        request,
        obj=signage,
        return_url=return_url
    )


@permission_required('visual_signage.add_signage')
def create_modal_view(request: WSGIRequest) -> TemplateResponse:
    return _modal_view(request)


@permission_required('visual_signage.change_signage')
def update_modal_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    return _modal_view(request, pk)


def _modal_view(request: WSGIRequest, pk: int = 0) -> TemplateResponse:
    signage = get_object_or_404(models.Signage, pk=pk)

    dg.glue_model_object(request, 'signage', signage)

    context_data = {
        'signage': signage
    }

    return TemplateResponse(
        request,
        context=context_data,
        template='metric/visual/signage/modal/content/form.html'
    )


@permission_required('visual_signage.add_signage')
def create_view(request: WSGIRequest) -> TemplateResponse:
    return _form_view(request)


@permission_required('visual_signage.change_signage')
def update_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    return _form_view(request, pk)


def _form_view(request: WSGIRequest, pk: int = 0) -> TemplateResponse|HttpResponseRedirect:
    signage = get_object_or_null_obj(models.Signage, pk=pk)

    dg.glue_model_object(request, 'signage', signage, 'view')

    if request.method == 'POST':
        form = forms.SignageForm(request.POST, instance=signage)

        if form.is_valid():
            signage, _ = signage.services.save_model_obj(**form.cleaned_data)
            add_form_activity(signage, pk, request.user)

            return redirect(
                request.GET.get(
                    'return_url',
                    reverse('metric:visual:signage:page:list')
                )
            )

        show_form_errors(request, form)
    else:
        form = forms.SignageForm(instance=signage)

    return portal_views.form_view(
        request,
        form=form,
        obj=signage,
        template='metric/visual/signage/page/form_page.html'
    )
