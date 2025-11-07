from __future__ import annotations

import json

from django_spire.knowledge.entry.version.block.choices import BlockTypeChoices
from django_spire.knowledge.entry.version.block.data.text_data import \
    TextEditorBlockData
from django_spire.knowledge.entry.version.block.models import EntryVersionBlock
from django_spire.knowledge.entry.version.tests.factories import \
    create_test_entry_version


def create_test_block_form_data(**kwargs) -> dict:
    data = {
        'block_order': 0,
        'block_type': BlockTypeChoices.TEXT,
        'block_data': {'text': 'test text'},
        'block_tunes': {}
    }

    data.update(kwargs)
    return data


def create_test_version_block(**kwargs) -> EntryVersionBlock:
    data = {
        'version': create_test_entry_version(),
        'order': 1,
        'type': BlockTypeChoices.TEXT,
        '_block_data': json.dumps({}),
        '_text_data': ''
    }

    data.update(kwargs)
    version_block = EntryVersionBlock.objects.create(**data)
    version_block.editor_js_block_data = TextEditorBlockData(
        text='',
    )
    version_block.save()

    return version_block
