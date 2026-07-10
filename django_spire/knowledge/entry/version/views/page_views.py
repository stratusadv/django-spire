from __future__ import annotations

import json

from typing import TYPE_CHECKING

from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse

from django_spire.auth.controller.controller import AppAuthController
from django_spire.knowledge.collection.models import Collection
from django_spire.knowledge.entry.models import Entry
from django_spire.knowledge.entry.navigation import EntryNavigation
from django_spire.knowledge.entry.version.models import EntryVersion

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


@AppAuthController('knowledge').permission_required('can_view')
def editor_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    entry_version = get_object_or_404(EntryVersion.objects.prefetch_blocks(), pk=pk)

    entry = entry_version.entry
    top_level_collection = entry.top_level_collection
    version_blocks = entry_version.blocks.format_for_editor()

    nav = EntryNavigation()
    nav.page_title = str(entry)
    nav.page_description = 'Detail View'

    breadcrumbs = []
    temp_collection = entry_version.entry.collection
    while temp_collection.parent:
        breadcrumbs.append(
            {
                'name': str(temp_collection.parent),
                'view_name': 'django_spire:knowledge:collection:page:top_level',
                'view_kwargs': {'pk': temp_collection.parent.pk},
            }
        )
        temp_collection = temp_collection.parent

    for crumb in reversed(breadcrumbs):
        nav.breadcrumbs.add(**crumb)

    nav.breadcrumbs.add(
        name=str(entry_version.entry.collection),
        view_name='django_spire:knowledge:collection:page:top_level',
        view_kwargs={'pk': entry_version.entry.collection.pk},
    )
    nav.breadcrumbs.add(str(entry))
    context = nav.as_context()
    context['entry'] = entry
    context['current_version'] = entry_version
    context['collection'] = top_level_collection
    context['version_blocks'] = json.dumps(list(version_blocks))
    context['collection_tree_json'] = Collection.services.transformation.to_hierarchy_json(
        request=request, parent_id=top_level_collection.id
    )

    return TemplateResponse(
        request,
        context=context,
        template='django_spire/knowledge/entry/version/page/editor_page.html',
    )
