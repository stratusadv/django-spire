from __future__ import annotations

from typing import TYPE_CHECKING

from django.shortcuts import redirect
from django.urls import reverse

import django_glue_old as dg

from django_spire.contrib.form.utils import show_form_errors
from django_spire.contrib.generic_views import portal_views
from django_spire.core.shortcuts import get_object_or_null_obj

from test_project.apps.file import forms, models

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest
    from django.http import HttpResponseRedirect
    from django.template.response import TemplateResponse


def create_view(request: WSGIRequest) -> TemplateResponse | HttpResponseRedirect:
    return _form_view(request, pk=None)


def update_view(request: WSGIRequest, pk: int) -> TemplateResponse | HttpResponseRedirect:
    return _form_view(request, pk=pk)


def _form_view(request: WSGIRequest, pk: int | None) -> TemplateResponse | HttpResponseRedirect:
    file_example = get_object_or_null_obj(models.FileExample, pk=pk)

    dg.glue_model_object(request, 'file_example', file_example)

    if request.method == 'POST':
        form = forms.FileExampleForm(request.POST, files=request.FILES, instance=file_example)

        if form.is_valid():
            file_example = form.save()
            file_example.services.processor.save_files(**form.cleaned_data)

            return redirect(
                reverse('file:page:detail', kwargs={'pk': file_example.pk})
            )

        show_form_errors(request, form)

    context_data = {
        'file_example': file_example,
    }

    return portal_views.template_view(
        request,
        page_title='Update File Example' if pk else 'Create File Example',
        page_description='',
        breadcrumbs=file_example.breadcrumbs(),
        context_data=context_data,
        template='file/page/form_page.html',
    )
