from __future__ import annotations

from typing import TYPE_CHECKING

from django.core.handlers.wsgi import WSGIRequest
from django_spire.knowledge.intelligence.bots.entry_search_llm_bot import EntrySearchBot
from django_spire.knowledge.intelligence.intel.entry_intel import EntriesIntel
from django_spire.knowledge.intelligence.intel.message_intel import KnowledgeMessageIntel
from django_spire.knowledge.intelligence.decoders.collection_decoder import CollectionDecoder
from django_spire.knowledge.intelligence.decoders.entry_decoder import get_entry_decoder

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest
    from dandy.llm.request.message import MessageHistory


def knowledge_search_workflow(
        request: WSGIRequest,
        user_input: str,
        message_history: MessageHistory,
) -> KnowledgeMessageIntel | None:
    collection_decoder = CollectionDecoder()
    collections = collection_decoder.process(user_input).values

    if collections[0] is None:
        return None

    entries = []

    for collection in collections:
        if collection.entry_count > 0:
            entry_decoder = get_entry_decoder(collection=collection)

            entries.extend(entry_decoder.process(user_input).values)

    entries = [entry for entry in entries if entry is not None]

    if not entries:
        return None

    entries_intel = EntriesIntel(entry_intel_list=[])

    for entry in entries:
        entries_intel.append(
            EntrySearchBot().process(user_input=user_input, entry=entry)
        )

    return KnowledgeMessageIntel(body=f'Entries: {entries_intel}', entries_intel=entries_intel)
