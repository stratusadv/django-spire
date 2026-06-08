from __future__ import annotations

from typing import TYPE_CHECKING

from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.urls import reverse

from django_spire.contrib.form.tools import show_form_errors
from django_spire.contrib.shortcuts import get_object_or_null_obj
from django_spire.history.activity.utils import add_form_activity

import django_glue as dg

from test_project.app.sync.registry import MODEL_FORM_MAP

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest
    from django.http import HttpResponseRedirect


def create_form_view(request: WSGIRequest, model: str) -> TemplateResponse:
    return _form_view(request, model)


def update_form_view(request: WSGIRequest, model: str, pk: int) -> TemplateResponse:
    return _form_view(request, model, pk)


def _form_view(
    request: WSGIRequest, model_name: str, pk: int = 0
) -> TemplateResponse | HttpResponseRedirect:
    if model_name not in MODEL_FORM_MAP:
        raise PermissionDenied

    model_cls, form_cls = MODEL_FORM_MAP[model_name]
    obj = get_object_or_null_obj(model_cls, pk=pk)

    dg.glue_model_object(request, model_name, obj, 'view')

    if request.method == 'POST':
        form = form_cls(request.POST, instance=obj)

        if form.is_valid():
            obj = form.save()
            add_form_activity(obj, pk, request.user)

            return redirect(
                request.GET.get(
                    'return_url',
                    reverse('sync:page:detail', kwargs={'model': model_name, 'pk': obj.pk}),
                )
            )

        show_form_errors(request, form)
    else:
        form = form_cls(instance=obj)

    return TemplateResponse(
        request,
        context={
            'form': form,
            'obj': obj,
            'page_title': model_name.capitalize(),
            'page_description': 'Edit' if pk else 'Create',
            'breadcrumbs': [
                {'name': model_name.capitalize(), 'href': None},
                {'name': 'Edit' if pk else 'Create', 'href': None},
            ],
        },
        template=f'sync/page/{model_name}_form_page.html',
    )
