from __future__ import annotations

import json

from django.core.handlers.wsgi import WSGIRequest
from django.db.models import F, Prefetch
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.urls import reverse

from django_spire.auth.controller.controller import AppAuthController
from django_spire.contrib.generic_views import portal_views
from django_spire.knowledge.entry.version.block.models import EntryVersionBlock
from django_spire.knowledge.entry.version.models import EntryVersion


@AppAuthController('knowledge').permission_required('can_view')
def detail_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    entry_version = get_object_or_404(EntryVersion.objects.prefetch_blocks(),pk=pk)

    entry = entry_version.entry
    version_blocks = entry_version.blocks.format_for_editor()

    def breadcrumbs_func(breadcrumbs):
        breadcrumbs.add_breadcrumb(
            name='Knowledge',
            href=reverse('django_spire:knowledge:page:home')
        )
        collection = entry.collection
        breadcrumbs.add_breadcrumb(
            name=f'{collection.name}'
        )
        breadcrumbs.add_breadcrumb(
            name=f'{entry.name}',
        )

    return portal_views.detail_view(
        request,
        obj=entry,
        breadcrumbs_func=breadcrumbs_func,
        context_data={
            'entry': entry,
            'current_version': entry_version,
            'version_blocks': json.dumps(list(version_blocks)),
        },
        template='django_spire/knowledge/entry/version/page/detail_page.html',
    )
