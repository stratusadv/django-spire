from __future__ import annotations

from typing_extensions import TYPE_CHECKING

from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse

from django_spire.form.utils import show_form_errors
from django_spire.views import portal_views
from django_spire.shortcuts import get_object_or_null_obj
from django_spire.history.utils import add_form_activity

from examples.placeholder import forms, models

from django_glue.glue import glue_model

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest
    from django.template.response import TemplateResponse


def placeholder_delete_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    placeholder = get_object_or_404(models.Placeholder, pk=pk)

    return portal_views.delete_form_view(
        request,
        obj=placeholder,
        return_url=request.GET.get(
            'return_url',
            reverse('placeholder:page:list')
        )
    )


def placeholder_detail_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    placeholder = get_object_or_404(models.Placeholder, pk=pk)

    context_data = {
        'placeholder': placeholder,
    }

    return portal_views.detail_view(
        request,
        obj=placeholder,
        context_data=context_data,
        template='placeholder/page/placeholder_detail_page.html'
    )


def placeholder_form_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    placeholder = get_object_or_null_obj(models.Placeholder, pk=pk)

    glue_model(request, 'placeholder', placeholder, 'view')

    if request.method == 'POST':
        form = forms.PlaceholderForm(request.POST, instance=placeholder)

        if form.is_valid():
            placeholder = form.save()
            add_form_activity(placeholder, pk, request.user)

            return redirect(
                request.GET.get(
                    'return_url',
                    reverse('placeholder:page:list')
                )
            )

        show_form_errors(request, form)
    else:
        form = forms.PlaceholderForm(instance=placeholder)

    return portal_views.form_view(
        request,
        form=form,
        obj=placeholder,
        template='placeholder/page/placeholder_form_page.html'
    )


def placeholder_list_view(request: WSGIRequest) -> TemplateResponse:
    context_data = {
        'placeholders': models.Placeholder.objects.all()
    }

    return portal_views.list_view(
        request,
        model=models.Placeholder,
        context_data=context_data,
        template='placeholder/page/placeholder_list_page.html'
    )
