from dandy.llm import MessageHistory
from dandy.workflow import BaseWorkflow

from django_spire.knowledge.intelligence.bots.entry_search_llm_bot import EntrySearchLlmBot
from django_spire.knowledge.intelligence.intel.collection_intel import CollectionIntel
from django_spire.knowledge.intelligence.intel.entry_intel import EntriesIntel, EntryIntel
from django_spire.knowledge.intelligence.maps.collection_map import get_collection_map_class
from django_spire.knowledge.intelligence.intel.message_intel import KnowledgeMessageIntel
from django_spire.knowledge.intelligence.maps.entry_map import get_entry_map_class


class KnowledgeWorkflow(BaseWorkflow):
    @classmethod
    def process(
            cls,
            user_input: str,
    ) -> KnowledgeMessageIntel:
        CollectionMap = get_collection_map_class()

        collections = CollectionMap.process(
            user_input,
        )

        entries = []

        if collections[0] is None:
            return KnowledgeMessageIntel(
                body=(
                    'There was no knowledge related to your request. Please reword it '
                    'and try again.'
                )
            )

        for collection in collections:
            if collection.entry_count > 0:

                EntryMap = get_entry_map_class(
                    collection=collection
                )

                entries.extend(EntryMap.process(user_input))

        if entries:
            entries_intel = EntriesIntel(
                entry_intel_list=[
                    EntryIntel(
                        body=EntrySearchLlmBot.process(
                            user_input=user_input,
                            entry=entry
                        ),
                        collection_intel=CollectionIntel(
                            name=entry.collection.name
                        )
                    ) for entry in entries
                ]
            )

            return KnowledgeMessageIntel(body=f'Entries: {entries_intel}')

        return KnowledgeMessageIntel(
            body=(
                'There was no knowledge related to your request. Please reword it and '
                'try again.'
            )
        )
