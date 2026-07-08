from __future__ import annotations

from django_glue import Glue

from typing import TYPE_CHECKING

from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import reverse

from django_spire.auth.controller.controller import AppAuthController
from django_spire.auth.group.models import AuthGroup
from django_spire.contrib.form.tools import show_form_errors
from django_spire.contrib.shortcuts import get_object_or_null_obj
from django_spire.knowledge.collection.models import Collection, CollectionGroup
from django_spire.knowledge.collection.forms import CollectionForm
from django_spire.knowledge.collection.navigation import CollectionNavigation

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


@AppAuthController('knowledge').permission_required('can_add')
def form_view(
    request: WSGIRequest, pk: int = 0, parent_pk: int | None = None
) -> TemplateResponse | HttpResponseRedirect:
    collection = get_object_or_null_obj(Collection, pk=pk)

    nav = CollectionNavigation()
    nav.page_title = 'Collection'
    nav.page_description = 'Edit' if pk else 'Create'
    nav.breadcrumbs.add('Collections', 'django_spire:knowledge:page:home')
    nav.breadcrumbs.add('Edit' if pk else 'Create')

    context = nav.as_context()

    if request.method == 'POST':
        form = CollectionForm(request.POST, instance=collection)

        if form.is_valid():
            collection, _ = collection.services.save_model_obj(**form.cleaned_data)

            CollectionGroup.services.factory.replace_groups(
                request=request, group_pks=dict(request.POST).get('groups'), collection=collection
            )

            collection.services.tag.process_and_set_tags()

            if collection.parent_id:
                return_url = reverse(
                    'django_spire:knowledge:collection:page:top_level',
                    kwargs={'pk': collection.services.tool.get_root_collection_pk()},
                )
            else:
                return_url = reverse('django_spire:knowledge:page:home')

            return HttpResponseRedirect(return_url)

        show_form_errors(request, form)
    else:
        form = CollectionForm(instance=collection, initial={'parent': parent_pk})

    context['form'] = form
    context['collection'] = collection
    context['collection_parent_pk'] = parent_pk
    context['group_ids'] = (
        list(collection.groups.all().values_list('auth_group_id', flat=True))
        if collection.id
        else []
    )
    return TemplateResponse(
        request, context=context, template='django_spire/knowledge/collection/page/form_page.html'
    )
