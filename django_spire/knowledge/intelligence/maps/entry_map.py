from __future__ import annotations

from dandy import Decoder

from django_spire.knowledge.collection.models import Collection


def get_entry_map_class(collection: Collection) -> type[Decoder]:
    class EntryMap(Decoder):
        mapping_keys_description = 'Knowledge Entries'
        mapping = {
            **{
                entry.name: entry
                for entry in collection.entries.all()
              },
            'No Matching Knowledge Entries': None
        }

    return EntryMap
