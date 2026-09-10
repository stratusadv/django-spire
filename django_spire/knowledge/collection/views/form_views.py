from __future__ import annotations

from typing import TYPE_CHECKING

from django.template.response import TemplateResponse
from django_glue import Glue

from django_spire.auth.permissions.decorators import permission_required
from django_spire.contrib.shortcuts import get_object_or_null_obj
from django_spire.knowledge.collection.breadcrumbs import add_collection_chain_breadcrumbs
from django_spire.knowledge.collection.forms import CollectionForm
from django_spire.knowledge.collection.models import Collection
from django_spire.knowledge.collection.navigation import CollectionNavigation

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


@permission_required('django_spire_knowledge.add_collection')
def form_view(request: WSGIRequest, pk: int = 0, parent_pk: int | None = None) -> TemplateResponse:
    collection = get_object_or_null_obj(Collection, pk=pk)

    nav = CollectionNavigation()
    nav.page_title = 'Collection'
    nav.page_description = 'Edit' if pk else 'Create'

    if collection.parent or parent_pk:
        parent_collection = get_object_or_null_obj(
            Collection, pk=parent_pk or collection.parent.pk
        )

        add_collection_chain_breadcrumbs(nav.breadcrumbs, parent_collection)

    if pk:
        nav.breadcrumbs.add(
            name=str(collection),
            view_name='django_spire:knowledge:collection:page:top_level',
            view_kwargs={'pk': pk},
        )

    nav.breadcrumbs.add('Edit' if pk else 'Create')

    form = CollectionForm(
        instance=collection,
        initial={'parent': collection.parent.pk if collection.parent else parent_pk},
    )

    Glue.form(request, 'collection_form', form, Glue.Access.CHANGE)

    return TemplateResponse(
        request,
        context=nav.as_context() | {
            'collection': collection,
            'collection_parent_pk': parent_pk,
        },
        template='django_spire/knowledge/collection/page/form_page.html',
    )
