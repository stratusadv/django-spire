from __future__ import annotations

from django.shortcuts import get_object_or_404
from django.urls import reverse

from django_spire.auth.controller.controller import AppAuthController
from django_spire.contrib import Breadcrumbs
from django_spire.contrib.generic_views import portal_views
from django_spire.knowledge.collection.models import Collection
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest
    from django.template.response import TemplateResponse


@AppAuthController('knowledge').permission_required('can_view')
def top_level_collection_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    collection = get_object_or_404(Collection, pk=pk)

    breadcrumbs = Breadcrumbs()
    breadcrumbs.add_breadcrumb('Knowledge', reverse('django_spire:knowledge:page:home'))
    breadcrumbs.add_base_breadcrumb(collection)

    return portal_views.template_view(
        request,
        page_title='Knowledge Collection',
        page_description='',
        breadcrumbs=breadcrumbs,
        context_data={
            'collection': collection,
            'collection_tree_json': Collection.services.transformation.to_hierarchy_json(
                request=request, parent_id=collection.id
            ),
        },
        template='django_spire/knowledge/collection/page/display_page.html',
    )


@AppAuthController('knowledge').permission_required('can_delete')
def delete_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    collection = get_object_or_404(Collection, pk=pk)

    if collection.parent:
        return_url = request.GET.get(
            'return_url',
            reverse(
                'django_spire:knowledge:collection:page:top_level',
                kwargs={'pk': collection.parent_id}
            )
        )
    else:
        return_url = request.GET.get('return_url', reverse('django_spire:knowledge:page:home'))

    return portal_views.delete_form_view(
        request,
        obj=collection,
        delete_func=collection.services.processor.set_deleted,
        return_url=return_url
    )
