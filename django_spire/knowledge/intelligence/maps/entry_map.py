from typing import Type

from dandy.llm import BaseLlmMap
from dandy.map import Map

from django_spire.knowledge.collection.models import Collection


def get_entry_map_class(collection: Collection) -> Type[BaseLlmMap]:
    class EntryMap(BaseLlmMap):
        map_keys_description = 'Knowledge Entries'
        map = Map({
            **{
                entry.name: entry
                for entry in collection.entries.all()
              },
            **{'No Matching Knowledge Entries': None}
        })

    return EntryMap
