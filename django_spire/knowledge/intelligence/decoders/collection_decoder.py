from __future__ import annotations

from dandy import Decoder

from django_spire.knowledge.collection.models import Collection


def get_collection_decoder() -> Decoder:
    class CollectionDecoder(Decoder):
        mapping_keys_description = 'Knowledge Collection Titles'
        mapping = {
            **{
                f'{collection.name}: {collection.description}': collection
                for collection in Collection.objects.all().annotate_entry_count()
            },
            'No Matching Knowledge Collection Titles': None,
        }

    return CollectionDecoder()