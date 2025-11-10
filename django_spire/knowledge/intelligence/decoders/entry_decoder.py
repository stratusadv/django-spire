from __future__ import annotations

from dandy import Decoder

from django_spire.knowledge.collection.models import Collection


def get_entry_decoder(collection: Collection) -> Decoder:
    class EntryDecoder(Decoder):
        mapping_keys_description = 'Knowledge Entries Tags'
        mapping = {
            **{
                f'{entry.tag_set}': entry
                for entry in collection.entries.all()
              },
            'No Matching Knowledge Entries': None
        }

    return EntryDecoder()
