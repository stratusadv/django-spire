import json

from django_spire.knowledge.entry.block.choices import BlockTypeChoices
from django_spire.knowledge.entry.block.models import EntryVersionBlock
from django_spire.knowledge.entry.tests.factories import create_test_entry_version


def create_test_version_block(**kwargs) -> EntryVersionBlock:
    data = {
        'version': create_test_entry_version(),
        'order': 1,
        'type': BlockTypeChoices.TEXT,
        '_block_data': json.dumps({}),
        '_text_data': ''
    }
    data.update(kwargs)
    return EntryVersionBlock.objects.create(**data)
