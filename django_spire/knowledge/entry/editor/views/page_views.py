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
                version=current_version,
                block_type=BlockTypeChoices.TEXT,
                order=0
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
                    {
                        **model_to_dict(
                            version_block,
                            fields=['id', 'order', 'type'],
                        ),
                        'is_deleted': version_block.is_deleted,
                        'block': {
                            'value': version_block.block.value,
                            'type': version_block.block.type,
                            'update_template_rendered': render_to_string(
                                request=request,
                                context={
                                    'version_block': version_block,
                                    'value': version_block.block.value,
                                },
                                template_name=version_block.block.update_template,
                            )
                        }
                    }
                    for version_block in version_blocks
                ]
            ),
            'version_blocks': version_blocks,
            'block_types': BlockTypeChoices,
        },
        template='django_spire/knowledge/entry/editor/page/editor_page.html',
    )
