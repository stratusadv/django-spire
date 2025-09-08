import json

from django_spire.knowledge.entry.version.block.blocks.text_block import TextBlock
from django_spire.knowledge.entry.version.block.choices import BlockTypeChoices
from django_spire.knowledge.entry.version.block.models import EntryVersionBlock
from django_spire.knowledge.entry.version.tests.factories import \
    create_test_entry_version


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
    version_block.block = TextBlock(value='', type=BlockTypeChoices.TEXT)
    version_block.save()

    return version_block
