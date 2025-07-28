from django_spire.auth.user.models import AuthUser
from django_spire.knowledge.collection.models import Collection
from django_spire.knowledge.entry.block.models import EntryVersionBlock
from django_spire.knowledge.entry.choices import EntryVersionTypeChoices
from django_spire.knowledge.entry.editor.blocks.heading_block import HeadingBlock
from django_spire.knowledge.entry.editor.blocks.sub_heading_block import SubHeadingBlock
from django_spire.knowledge.entry.editor.blocks.text_block import TextBlock

LADDER_SAFETY_COLLECTION_NAME = 'Ladder Safety'

SEED_COLLECTIONS = {
    'Health and Safety': {
        'description': 'Information on health and safety',
        'sub_collections': {
            LADDER_SAFETY_COLLECTION_NAME: 'Information on ladder safety',
            'Fire Safety': 'Information on fire safety'
        },
        'General': 'General knowledge about the company',
    }
}

for idx, (key, value) in enumerate(SEED_COLLECTIONS.items(), start=1):
    new_collection = Collection.objects.create(
        name=key,
        description=value['description'],
        order=idx
    )

    if 'sub_collections' in value:
        for sub_idx, (sub_key, sub_value) in enumerate(value['sub_collections'].items(), start=1):
            new_sub_collection = Collection.objects.create(
                name=sub_key,
                description=sub_value,
                parent=new_collection,
                order=sub_idx
            )

SEED_ENTRIES = [
    {
        'collection': LADDER_SAFETY_COLLECTION_NAME,
        'name': 'Proper Ladder Safety',
        'blocks': [
            HeadingBlock(value='Proper Ladder Safety'),
            SubHeadingBlock(value='What is to High?'),
            TextBlock(value='High ladders are a falling risk and all workers should take time to understand the risks of using them.'),
            TextBlock(value='When climbing up a ladder below a certain height, make sure to confirm the ladder is on solid ground and leaning against a solid support.'),
            SubHeadingBlock(value='What is to Low?'),
            TextBlock(value='Low ladders may appear to be more safe but pose some risks.'),
            TextBlock(value='They are very much a tripping hazard and should be placed in safe places when people are done working with them.')
        ]
    }
]

for entry_idx, entry in enumerate(SEED_ENTRIES, start=1):
    collection = Collection.objects.get(name=entry['collection'])
    new_entry = collection.entries.create(
        name=entry['name'],
        order=entry_idx
    )
    new_entry_version = new_entry.versions.create(
        status=EntryVersionTypeChoices.PUBLISHED,
        author=AuthUser.objects.earliest('pk')
    )

    new_entry.current_version = new_entry_version
    new_entry.save()

    for block_idx, block in enumerate(entry['blocks'], start=1):
        new_entry_version_block = EntryVersionBlock()
        new_entry_version_block.block = block
        new_entry_version_block.version = new_entry_version
        new_entry_version_block.order = block_idx
        new_entry_version_block.save()
