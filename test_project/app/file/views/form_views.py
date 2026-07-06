from __future__ import annotations

from typing import TYPE_CHECKING

from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.urls import reverse

from django_glue import Glue

from django_spire.contrib.form.tools import show_form_errors

from django_spire.contrib.shortcuts import get_object_or_null_obj

from test_project.app.file import forms, models
from test_project.app.file.forms import FileExampleForm

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest
    from django.http import HttpResponseRedirect


def create_view(request: WSGIRequest) -> TemplateResponse | HttpResponseRedirect:
    return _form_view(request, pk=None)


def update_view(request: WSGIRequest, pk: int) -> TemplateResponse | HttpResponseRedirect:
    return _form_view(request, pk=pk)


def _form_view(request: WSGIRequest, pk: int | None) -> TemplateResponse | HttpResponseRedirect:
    file_example = get_object_or_null_obj(models.FileExample, pk=pk)

    Glue.model(request, 'file_example', file_example)

    if request.method == 'POST':
        form = forms.FileExampleForm(request.POST, files=request.FILES, instance=file_example)

        if form.is_valid():
            file_example = form.save()
            file_example.services.processor.save_files(**form.cleaned_data)

            return redirect(reverse('file:page:detail', kwargs={'pk': file_example.pk}))

        show_form_errors(request, form)

    else:
        form = forms.FileExampleForm(instance=file_example)

    Glue.form(request, 'file_example_form', target=form, access=Glue.Access.DELETE)

    context = {'file_example': file_example}
    context['page_title'] = 'Update File Example' if pk else 'Create File Example'
    context['page_description'] = ''
    context['breadcrumbs'] = [
        {'name': 'File Examples', 'href': reverse('file:page:list')},
        {'name': 'Update' if pk else 'Create', 'href': None},
    ]
    return TemplateResponse(request, 'file/page/form_page.html', context=context)
