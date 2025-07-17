from typing import List

from dandy.workflow import BaseWorkflow

from django_spire.knowledge.collection.models import Collection
from django_spire.knowledge.intelligence.intel.collection_intel import CollectionIntel
from django_spire.knowledge.intelligence.intel.entry_intel import EntriesIntel, EntryIntel
from django_spire.knowledge.intelligence.maps.collection_map import get_collection_map_class
from django_spire.knowledge.intelligence.intel.message_intel import KnowledgeMessageIntel
from django_spire.knowledge.intelligence.maps.entry_map import get_entry_map_class


class KnowledgeWorkflow(BaseWorkflow):
    @classmethod
    def process(
            cls,
            user_input: str
    ) -> KnowledgeMessageIntel:
        CollectionMap = get_collection_map_class()

        collections = CollectionMap.process(
            user_input
        )

        entries = []

        for collection in collections:
            EntryMap = get_entry_map_class(
                collection=collection
            )

            entries.extend(
                EntryMap.process(
                    user_input
                )
            )

        entries_intel = EntriesIntel(
            entry_intel_list=[
                EntryIntel(
                    collection_intel=CollectionIntel(
                        name=entry.collection.name
                    )
                ) for entry in entries
            ]
        )

        return KnowledgeMessageIntel(
            body=f'Entries: {entries_intel}'
        )

    def get_collections(self) -> List[Collection]:
        pass
