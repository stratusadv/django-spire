from __future__ import annotations

import json

from typing import TYPE_CHECKING

from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse

from django_spire.auth.permissions.decorators import permission_required
from django_spire.knowledge.collection.breadcrumbs import add_collection_chain_breadcrumbs
from django_spire.knowledge.collection.models import Collection
from django_spire.knowledge.entry.models import Entry
from django_spire.knowledge.entry.navigation import EntryNavigation
from django_spire.knowledge.entry.version.models import EntryVersion

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


@permission_required('django_spire_knowledge.view_collection')
def editor_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    entry_version = get_object_or_404(EntryVersion.objects.prefetch_blocks(), pk=pk)

    entry = entry_version.entry
    top_level_collection = entry.top_level_collection
    version_blocks = entry_version.blocks.format_for_editor()

    nav = EntryNavigation()
    nav.page_title = str(entry)
    nav.page_description = 'Detail View'

    add_collection_chain_breadcrumbs(nav.breadcrumbs, entry_version.entry.collection)

    nav.breadcrumbs.add(str(entry))

    return TemplateResponse(
        request,
        context=nav.as_context() | {
            'entry': entry,
            'current_version': entry_version,
            'collection': top_level_collection,
            'version_blocks': json.dumps(list(version_blocks)),
            'collection_tree_json': Collection.services.transformation.to_hierarchy_json(
                request=request, parent_id=top_level_collection.id
            ),
        },
        template='django_spire/knowledge/entry/version/page/editor_page.html',
    )
