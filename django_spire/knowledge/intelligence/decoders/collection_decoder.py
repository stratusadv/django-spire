from __future__ import annotations

from dandy import Decoder

from django_spire.knowledge.collection.models import Collection


def generate_collection_mapping() -> dict:
    return {
        **{
            f'{collection.name}: {collection.description}': collection
            for collection in Collection.objects.all().annotate_entry_count()
        },
        'No Matching Knowledge Collection Titles': None,
    }


class CollectionDecoder(Decoder):
    mapping_keys_description = 'Knowledge Collection Titles'
    mapping = generate_collection_mapping()
