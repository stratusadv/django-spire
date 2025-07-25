import json

from django.contrib.auth.decorators import login_required
from django.core.handlers.wsgi import WSGIRequest
from django.forms import model_to_dict
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.template.response import TemplateResponse

from django_spire.contrib import Breadcrumbs
from django_spire.contrib.generic_views import portal_views
from django_spire.knowledge.entry.block.choices import BlockTypeChoices
from django_spire.knowledge.entry.block.models import EntryVersionBlock
from django_spire.knowledge.entry.models import Entry


@login_required()
def edit_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    entry = get_object_or_404(Entry, pk=pk)
    current_version = entry.current_version
    version_blocks = current_version.blocks.active().order_by('order')

    if version_blocks.count() == 0:
        version_blocks = [
            EntryVersionBlock.services.factory.create_blank_block(
                entry_version=current_version,
                block_type=BlockTypeChoices.TEXT,
                order=1
            )
        ]

    breadcrumbs = Breadcrumbs()
    breadcrumbs.add_breadcrumb(name=f'Edit {entry.name}')

    return portal_views.template_view(
        request,
        page_title=f'Edit {entry.name}',
        page_description=f'Edit {entry.name}',
        breadcrumbs=breadcrumbs,
        context_data={
            'entry': entry,
            'current_version': current_version,
            'version_blocks_json': json.dumps(
                [
                    version_block.to_dict()
                    for version_block in version_blocks
                ]
            ),
            'version_blocks': version_blocks,
            'block_types': BlockTypeChoices,
        },
        template='django_spire/knowledge/entry/editor/page/editor_page.html',
    )
