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

from test_project.apps.infinite_scrolling import forms, models

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest
    from django.http import HttpResponseRedirect


@permission_required('infinite_scrolling.delete_infinite_scrolling')
def delete_modal_form_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    infinite_scrolling = get_object_or_404(models.InfiniteScrolling, pk=pk)

    form_action = reverse(
        'infinite_scrolling:form:delete_modal',
        kwargs={'pk': pk}
    )

    def add_activity() -> None:
        infinite_scrolling.add_activity(
            user=request.user,
            verb='deleted',
            information=f'{request.user.get_full_name()} deleted a infinite_scrolling.'
        )

    fallback = reverse('infinite_scrolling:page:list')
    return_url = safe_redirect_url(request, fallback=fallback)

    return modal_views.dispatch_modal_delete_form_content(
        request,
        obj=infinite_scrolling,
        form_action=form_action,
        activity_func=add_activity,
        return_url=return_url,
    )


@permission_required('infinite_scrolling.delete_infinite_scrolling')
def delete_form_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    infinite_scrolling = get_object_or_404(models.InfiniteScrolling, pk=pk)

    return_url = request.GET.get(
        'return_url',
        reverse('infinite_scrolling:page:list')
    )

    return portal_views.delete_form_view(
        request,
        obj=infinite_scrolling,
        return_url=return_url
    )


def detail_modal_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    infinite_scrolling = get_object_or_404(models.InfiniteScrolling, pk=pk)

    dg.glue_model_object(request, 'infinite_scrolling', infinite_scrolling, 'view')

    context_data = {
        'infinite_scrolling': infinite_scrolling
    }

    return TemplateResponse(
        request,
        context=context_data,
        template='infinite_scrolling/modal/content/detail.html'
    )


@permission_required('infinite_scrolling.add_infinite_scrolling')
def create_modal_form_view(request: WSGIRequest) -> TemplateResponse:
    return _modal_form_view(request)


@permission_required('infinite_scrolling.change_infinite_scrolling')
def update_modal_form_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    return _modal_form_view(request, pk)


def _modal_form_view(request: WSGIRequest, pk: int = 0) -> TemplateResponse:
    infinite_scrolling = get_object_or_null_obj(models.InfiniteScrolling, pk=pk)

    dg.glue_model_object(request, 'infinite_scrolling', infinite_scrolling)

    if request.method == 'POST':
        form = forms.InfiniteScrollingForm(request.POST, instance=infinite_scrolling)

        if form.is_valid():
            infinite_scrolling.services.factory.save_model_obj(
                user=request.user,
                obj=infinite_scrolling,
                **form.cleaned_data
            )

            fallback = reverse('infinite_scrolling:page:list')
            return_url = safe_redirect_url(request, fallback=fallback)

            return redirect(return_url)

        show_form_errors(request, form)

    context_data = {
        'infinite_scrolling': infinite_scrolling
    }

    return TemplateResponse(
        request,
        context=context_data,
        template='infinite_scrolling/modal/content/form.html'
    )


@permission_required('infinite_scrolling.add_infinite_scrolling')
def create_form_view(request: WSGIRequest) -> TemplateResponse:
    return _form_view(request)


@permission_required('infinite_scrolling.change_infinite_scrolling')
def update_form_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    return _form_view(request, pk)


def _form_view(request: WSGIRequest, pk: int = 0) -> TemplateResponse|HttpResponseRedirect:
    infinite_scrolling = get_object_or_null_obj(models.InfiniteScrolling, pk=pk)

    dg.glue_model_object(request, 'infinite_scrolling', infinite_scrolling, 'view')

    if request.method == 'POST':
        form = forms.InfiniteScrollingForm(request.POST, instance=infinite_scrolling)

        if form.is_valid():
            infinite_scrolling = form.save()
            add_form_activity(infinite_scrolling, pk, request.user)

            return redirect(
                request.GET.get(
                    'return_url',
                    reverse('infinite_scrolling:page:list')
                )
            )

        show_form_errors(request, form)
    else:
        form = forms.InfiniteScrollingForm(instance=infinite_scrolling)

    return portal_views.form_view(
        request,
        form=form,
        obj=infinite_scrolling,
        template='infinite_scrolling/page/form_page.html'
    )
