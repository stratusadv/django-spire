from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib.auth.decorators import permission_required
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.urls import reverse

from django_spire.contrib.responses.json_response import success_json_response
from django_spire.core.redirect.safe_redirect import safe_redirect_url
from django_spire.core.shortcuts import get_object_or_null_obj
from django_spire.contrib.form.utils import show_form_errors
from django_spire.contrib.generic_views import portal_views, modal_views

import django_glue as dg

from test_project.apps.ordering import forms, models

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest
    from django.http import HttpResponseRedirect, JsonResponse


@permission_required('apps.change_appsordering')
def create_form_view(request: WSGIRequest) -> HttpResponseRedirect | TemplateResponse:
    duck = models.Duck()

    dg.glue_model_object(request, 'duck', duck, 'view')

    if request.method == 'POST':
        form = forms.DuckForm(request.POST, instance=duck)

        if form.is_valid():
            duck.services.save_model_obj(**form.cleaned_data)
            all_ducks = models.Duck.objects.active().order_by('order')
            duck.ordering_services.processor.move_to_position(
                destination_objects=all_ducks,
                position=duck.order
            )

            return redirect(
                request.GET.get(
                    'return_url',
                    reverse('ordering:page:demo')
                )
            )

        show_form_errors(request, form)
    else:
        form = forms.DuckForm(instance=duck)

    return portal_views.form_view(
        request,
        form=form,
        obj=duck,
        template='ordering/page/form_page.html'
    )


@permission_required('apps.delete_appsordering')
def delete_form_modal_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    duck = get_object_or_404(models.Duck, pk=pk)

    form_action = reverse(
        'ordering:form:delete_form_modal',
        kwargs={'pk': pk}
    )

    fallback = reverse(
        'ordering:page:demo'
    )

    return_url = safe_redirect_url(request, fallback=fallback)

    return modal_views.dispatch_modal_delete_form_content(
        request,
        obj=duck,
        form_action=form_action,
        activity_func=None,
        return_url=return_url,
    )


@permission_required('apps.change_appsordering')
def form_content_modal_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    duck = get_object_or_null_obj(models.Duck, pk=pk)
    action_url = reverse(
        'ordering:form:form',
        kwargs={'pk': pk}
    )
    unique_name = f'{duck.pk}_duck'

    if duck.id is None:
        duck = models.Duck()
        action_url = reverse(
            'ordering:form:create'
        )
        unique_name = 'duck'

    dg.glue_model_object(request, unique_name, duck)

    context_data = {
        'duck': duck,
        'action_url': action_url,
        'unique_name': unique_name
    }

    return TemplateResponse(
        request,
        context=context_data,
        template='ordering/modal/content/form_modal_content.html'
    )


@permission_required('apps.change_appsordering')
def form_view(request: WSGIRequest, pk: int) -> HttpResponseRedirect | TemplateResponse:
    duck = get_object_or_null_obj(models.Duck, pk=pk)

    dg.glue_model_object(request, 'duck', duck, 'view')

    if request.method == 'POST':
        form = forms.DuckForm(request.POST, instance=duck)

        if form.is_valid():
            duck.services.save_model_obj(**form.cleaned_data)

            return redirect(
                request.GET.get(
                    'return_url',
                    reverse('ordering:page:demo')
                )
            )

        show_form_errors(request, form)
    else:
        form = forms.DuckForm(instance=duck)

    return portal_views.form_view(
        request,
        form=form,
        obj=duck,
        template='ordering/page/form_page.html'
    )
