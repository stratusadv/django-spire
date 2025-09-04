from __future__ import annotations

import django_glue as dg

from typing import TYPE_CHECKING

from django.http import HttpResponseRedirect
from django.urls import reverse

from django_spire.auth.controller.controller import AppAuthController
from django_spire.contrib.form.utils import show_form_errors
from django_spire.contrib.generic_views import portal_views
from django_spire.core.shortcuts import get_object_or_null_obj
from django_spire.knowledge.collection.models import Collection
from django_spire.knowledge.collection.forms import CollectionForm

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest
    from django.template.response import TemplateResponse


# Don't like this method. Hard-coupled to view name.
@AppAuthController('knowledge').can_access_view()  # Gets view name and can create map in KnowledgeAuthController to match to permission.

# Provide basic default views, how can user (client devs) have special permissions on views?
@AppAuthController('knowledge').can_view()
@AppAuthController('knowledge').can_add()
@AppAuthController('knowledge').can_change()
@AppAuthController('knowledge').can_delete()

def form_view(
        request: WSGIRequest,
        pk: int = 0
) -> TemplateResponse | HttpResponseRedirect:
    collection = get_object_or_null_obj(Collection, pk=pk)

    dg.glue_model_object(request, unique_name='collection', model_object=collection)
    dg.glue_query_set(
        request,
        unique_name='collections',
        target=Collection.objects.active(),
        fields=['name']
    )

    if AppAuthController('knowledge', request).has_tacos():
        ...

    if request.method == 'POST':
        form = CollectionForm(request.POST, instance=collection)

        if form.is_valid():
            _, _ = collection.services.save_model_obj(**form.cleaned_data)

            return HttpResponseRedirect(
                reverse('django_spire:knowledge:collection:page:list')
            )

        show_form_errors(request, form)
    else:
        form = CollectionForm(instance=collection)

    return portal_views.form_view(
        request,
        form=form,
        obj=collection,
        context_data={
            'collection': collection
        },
        template='django_spire/knowledge/collection/page/form_page.html'
    )
