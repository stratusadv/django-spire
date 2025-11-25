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

import django_glue as dg

from test_project.apps.queryset_filtering import forms, models

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest
    from django.http import HttpResponseRedirect


@permission_required('test_project_queryset_filtering.delete_task')
def delete_modal_form_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    task = get_object_or_404(models.Task, pk=pk)

    form_action = reverse(
        'queryset_filtering:form:delete_modal',
        kwargs={'pk': pk}
    )

    def add_activity() -> None:
        task.add_activity(
            user=request.user,
            verb='deleted',
            device=request.device,
            information=f'{request.user.get_full_name()} deleted a task.'
        )

    fallback = reverse('queryset_filtering:page:list')
    return_url = safe_redirect_url(request, fallback=fallback)

    return modal_views.dispatch_modal_delete_form_content(
        request,
        obj=task,
        form_action=form_action,
        activity_func=add_activity,
        return_url=return_url,
    )


@permission_required('test_project_queryset_filtering.delete_task')
def delete_form_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    task = get_object_or_404(models.Task, pk=pk)

    return_url = request.GET.get(
        'return_url',
        reverse('queryset_filtering:page:list')
    )

    return portal_views.delete_form_view(
        request,
        obj=task,
        return_url=return_url
    )


@permission_required('test_project_queryset_filtering.add_task')
def create_modal_form_view(request: WSGIRequest) -> TemplateResponse:
    return _modal_form_view(request)


@permission_required('test_project_queryset_filtering.change_task')
def update_modal_form_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    return _modal_form_view(request, pk)


def _modal_form_view(request: WSGIRequest, pk: int = 0) -> TemplateResponse:
    task = get_object_or_null_obj(models.Task, pk=pk)

    dg.glue_model_object(request, 'task', task)

    context_data = {
        'task': task
    }

    return TemplateResponse(
        request,
        context=context_data,
        template='queryset_filtering/modal/content/queryset_filtering_modal_content.html'
    )


@permission_required('test_project_queryset_filtering.add_task')
def create_form_view(request: WSGIRequest) -> TemplateResponse:
    return _form_view(request)


@permission_required('test_project_queryset_filtering.change_task')
def update_form_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    return _form_view(request, pk)


def _form_view(request: WSGIRequest, pk: int = 0) -> TemplateResponse|HttpResponseRedirect:
    task = get_object_or_null_obj(models.Task, pk=pk)

    dg.glue_model_object(request, 'task', task)

    if request.method == 'POST':
        form = forms.TaskForm(request.POST, instance=task)

        if form.is_valid():
            task.services.save_model_obj(
                user=request.user,
                obj=task,
                **form.cleaned_data
            )

            return redirect(
                request.GET.get(
                    'return_url',
                    reverse('tabular:page:list')
                )
            )

        show_form_errors(request, form)
    else:
        form = forms.TaskForm(instance=task)

    return portal_views.form_view(
        request,
        form=form,
        obj=task,
        template='queryset_filtering/page/form_page.html'
    )
