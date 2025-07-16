from __future__ import annotations

from typing import TYPE_CHECKING

from django.http import HttpResponseRedirect
from django.urls import reverse

from django_spire.contrib.generic_views import portal_views
from django_spire.core.shortcuts import get_object_or_null_obj
from django_spire.knowledge.collection.models import Collection
from django_spire.knowledge.collection.forms import CollectionForm

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest
    from django.template.response import TemplateResponse


def form_view(
        request: WSGIRequest,
        pk: int = 0
) -> TemplateResponse | HttpResponseRedirect:
    collection = get_object_or_null_obj(Collection, pk=pk)

    if request.method == 'POST':
        form = CollectionForm(request.POST, instance=collection)

        if form.is_valid():
            created = Collection.services.save_model_obj(request.POST)

            return HttpResponseRedirect(
                reverse('django_spire:knowledge:collection:page:list')
            )
    else:
        form = CollectionForm(instance=collection)

    return portal_views.form_view(
        request,
        form=form,
        obj=collection,
        template='django_spire/knowledge/collection/page/form_page.html'
    )
