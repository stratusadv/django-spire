from __future__ import annotations

from dandy import Decoder

from django_spire.knowledge.collection.models import Collection


def get_collection_map_class() -> type[Decoder]:
    class CollectionMap(Decoder):
        mapping_keys_description = 'Knowledge Collection Titles'
        mapping = {
            **{
                collection.name: collection
                for collection in Collection.objects.all().annotate_entry_count()
            },
            'No Matching Knowledge Collection Titles': None
        }

    return CollectionMap
