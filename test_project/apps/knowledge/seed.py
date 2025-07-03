from django_spire.auth.user.models import AuthUser
from django_spire.knowledge.collection.models import Collection
from django_spire.knowledge.entry.block.models import EntryVersionBlock
from django_spire.knowledge.entry.choices import EntryVersionTypeChoices
from django_spire.knowledge.entry.editor.blocks.heading_block import HeadingBlock
from django_spire.knowledge.entry.editor.blocks.sub_heading_block import SubHeadingBlock
from django_spire.knowledge.entry.editor.blocks.text_block import TextBlock

SEED_COLLECTIONS = {
    'Health and Safety': {
        'description': 'Information on health and safety',
        'sub_collections': {
            'Ladder Safety': 'Information on ladder safety',
            'Fire Safety': 'Information on fire safety'
        },
        'General': 'General knowledge about the company',
    }
}

for key, value in SEED_COLLECTIONS.items():
    new_collection = Collection.objects.create(
        name=key,
        description=value['description'],
    )

    if 'sub_collections' in value:
        for sub_key, sub_value in value['sub_collections'].items():
            new_sub_collection = Collection.objects.create(
                name=sub_key,
                description=sub_value,
                parent=new_collection
            )

SEED_ENTRIES = [
    {
        'collection': 'Health and Safety',
        'name': 'Ladder Safety',
        'blocks': [
            HeadingBlock(value='Ladder Safety'),
            SubHeadingBlock(value='What is to High?'),
            TextBlock(value='High ladders are a falling risk and all workers should take time to understand the risks of using them.'),
            TextBlock(value='When climbing up a ladder below a certain height, make sure to confirm the ladder is on solid ground and leaning against a solid support.'),
            SubHeadingBlock(value='What is to Low?'),
            TextBlock(value='Low ladders may appear to be more safe but pose some risks.'),
            TextBlock(value='They are very much a tripping hazard and should be placed in safe places when people are done working with them.')
        ]
    }
]

for entry in SEED_ENTRIES:
    collection = Collection.objects.earliest('pk')
    new_entry = collection.entries.create(
        name=entry['name']
    )
    new_entry_version = new_entry.versions.create(
        status=EntryVersionTypeChoices.PUBLISHED,
        author=AuthUser.objects.earliest('pk')
    )

    new_entry.current_version = new_entry_version
    new_entry.save()

    for block in entry['blocks']:
        new_entry_version_block = EntryVersionBlock()
        new_entry_version_block.block = block
        new_entry_version_block.version = new_entry_version
        new_entry_version_block.save()