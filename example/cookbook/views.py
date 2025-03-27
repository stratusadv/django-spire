from __future__ import annotations

from typing_extensions import TYPE_CHECKING

from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse

from django_spire.core.shortcuts import get_object_or_null_obj
from django_spire.form.utils import show_form_errors
from django_spire.history.utils import add_form_activity
from django_spire.views import portal_views

import django_glue as dg

from example.cookbook import factories, forms, models
from example.cookbook.recipe.models import Recipe


if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest
    from django.template.response import TemplateResponse


def cookbook_delete_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    cookbook = get_object_or_404(models.Cookbook, pk=pk)

    return portal_views.delete_form_view(
        request,
        obj=cookbook,
        return_url=request.GET.get('return_url', reverse('cookbook:page:list')),
    )


def cookbook_detail_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    cookbook = get_object_or_404(models.Cookbook, pk=pk)

    context_data = {
        'cookbook': cookbook,
        'recipes': Recipe.objects.by_cookbook(pk)
    }

    return portal_views.detail_view(
        request,
        obj=cookbook,
        context_data=context_data,
        template='cookbook/page/cookbook_detail_page.html'
    )


def cookbook_form_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    cookbook = get_object_or_null_obj(models.Cookbook, pk=pk)

    dg.glue_model_object(request, 'cookbook', cookbook, 'view')
    dg.glue_query_set(request,  'recipe_queryset', Recipe.objects.active(), 'view')

    if request.method == 'POST':
        form = forms.CookbookForm(request.POST, instance=cookbook)

        if form.is_valid():
            cookbook = form.save()
            factories.link_cookbook_recipes(cookbook, form.cleaned_data['linked_recipes'])
            add_form_activity(cookbook, pk, request.user)
            return redirect(request.GET.get('return_url', reverse('cookbook:page:list')))

        show_form_errors(request, form)
    else:
        form = forms.CookbookForm(instance=cookbook)

    return portal_views.form_view(
        request,
        form=form,
        obj=cookbook,
        template='cookbook/page/cookbook_form_page.html'
    )


def cookbook_list_view(request: WSGIRequest) -> TemplateResponse:
    context_data = {
        'cookbooks': models.Cookbook.objects.all()
    }

    return portal_views.list_view(
        request,
        model=models.Cookbook,
        context_data=context_data,
        template='cookbook/page/cookbook_list_page.html'
    )
