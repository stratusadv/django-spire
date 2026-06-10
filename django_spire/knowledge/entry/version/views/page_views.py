from __future__ import annotations

import json

from typing import TYPE_CHECKING

from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.urls import reverse

from django_spire.auth.controller.controller import AppAuthController
from django_spire.knowledge.collection.models import Collection
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
    nav.breadcrumbs.add('Knowledge', reverse('django_spire:knowledge:page:home'))
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
