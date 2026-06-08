from __future__ import annotations

import json

from typing import TYPE_CHECKING

from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.urls import reverse

from django_spire.auth.controller.controller import AppAuthController
from django_spire.knowledge.collection.models import Collection
from django_spire.knowledge.entry.version.models import EntryVersion

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


@AppAuthController('knowledge').permission_required('can_view')
def editor_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    entry_version = get_object_or_404(EntryVersion.objects.prefetch_blocks(), pk=pk)

    entry = entry_version.entry
    top_level_collection = entry.top_level_collection
    version_blocks = entry_version.blocks.format_for_editor()

    context_data = {
        'entry': entry,
        'current_version': entry_version,
        'collection': top_level_collection,
        'version_blocks': json.dumps(list(version_blocks)),
        'collection_tree_json': Collection.services.transformation.to_hierarchy_json(
            request=request, parent_id=top_level_collection.id
        ),
    }

    context_data['page_title'] = str(entry)
    context_data['page_description'] = 'Detail View'
    context_data['breadcrumbs'] = [
        {'name': 'Knowledge', 'href': reverse('django_spire:knowledge:page:home')},
        {'name': str(entry), 'href': None},
    ]

    return TemplateResponse(
        request,
        context=context_data,
        template='django_spire/knowledge/entry/version/page/editor_page.html',
    )
