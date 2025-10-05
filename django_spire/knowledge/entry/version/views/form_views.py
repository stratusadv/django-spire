from __future__ import annotations

import json

from django.core.handlers.wsgi import WSGIRequest
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.urls import reverse

from django_spire.auth.controller.controller import AppAuthController
from django_spire.contrib import Breadcrumbs
from django_spire.contrib.generic_views import portal_views
from django_spire.knowledge.entry.version.block.choices import BlockTypeChoices
from django_spire.knowledge.entry.version.block.models import EntryVersionBlock
from django_spire.knowledge.entry.version.models import EntryVersion


@AppAuthController('knowledge').permission_required('can_change')
def update_form_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    current_version = get_object_or_404(EntryVersion, pk=pk)
    entry = current_version.entry
    version_blocks = current_version.blocks.active().order_by('order')

    if version_blocks.count() == 0:
        version_blocks = [
            EntryVersionBlock.services.factory.create_blank_block(
                entry_version=current_version,
                block_type=BlockTypeChoices.TEXT,
                order=0
            )
        ]

    breadcrumbs = Breadcrumbs()
    breadcrumbs.add_breadcrumb(name='Knowledge')
    breadcrumbs.add_breadcrumb(
        name='Collections',
        href=reverse('django_spire:knowledge:collection:page:list')
    )
    breadcrumbs.add_breadcrumb(
        name=entry.collection.name,
        href=reverse(
            'django_spire:knowledge:collection:page:detail',
            kwargs={'pk': entry.collection_id}
        )
    )
    breadcrumbs.add_breadcrumb(
        name=f'View {entry.name}',
        href=reverse(
            'django_spire:knowledge:entry:version:page:detail',
            kwargs={'pk': entry.current_version_id}
        )
    )
    breadcrumbs.add_breadcrumb(name=f'Edit {entry.name}')

    return portal_views.template_view(
        request,
        page_title=f'Edit {entry.name}',
        page_description=f'Edit {entry.name}',
        breadcrumbs=breadcrumbs,
        context_data={
            'entry': entry,
            'current_version': current_version,
            'version_blocks_json': EntryVersionBlock.services.transformation.objects_to_json(
                objects=version_blocks
            ),
            'version_blocks': version_blocks,
            'block_types': BlockTypeChoices,
        },
        template='django_spire/knowledge/entry/version/page/form_page.html',
    )
