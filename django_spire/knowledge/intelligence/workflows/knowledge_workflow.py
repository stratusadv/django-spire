from __future__ import annotations

from typing import TYPE_CHECKING

from django.core.handlers.wsgi import WSGIRequest

from django_spire.ai.chat.message_intel import DefaultMessageIntel, BaseMessageIntel
from django_spire.core.tag.intelligence.tag_set_bot import TagSetBot
from django_spire.knowledge.collection.models import Collection
from django_spire.knowledge.intelligence.bots.entry_search_llm_bot import EntrySearchBot
from django_spire.knowledge.intelligence.intel.entry_intel import EntriesIntel
from django_spire.knowledge.intelligence.intel.message_intel import KnowledgeMessageIntel

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest
    from dandy.llm.request.message import MessageHistory

NO_KNOWLEDGE_MESSAGE_INTEL = DefaultMessageIntel(
    text='Sorry, I could not find any information on that.'
)


def knowledge_search_workflow(
        request: WSGIRequest,
        user_input: str,
        message_history: MessageHistory | None = None,
) -> BaseMessageIntel | None:
    user_tag_set = TagSetBot().process(user_input)

    collections_scores = {}

    for collection in Collection.objects.all().annotate_entry_count():
        score = collection.services.tag.get_score_percentage_from_aggregated_tag_set_weighted(user_tag_set)
        if score > 0.05:
            collections_scores[collection] = score

    collections = sorted(
        collections_scores,
        key=collections_scores.get,
        reverse=True
    )[:5]

    entries_scores = {}

    for collection in collections:
        if collection.entry_count > 0:
            for entry in collection.entries.all():
                score = entry.services.tag.get_score_percentage_from_tag_set_weighted(user_tag_set)
                if score > 0.05:
                    entries_scores[entry] = score

    entries = sorted(
        entries_scores,
        key=entries_scores.get,
        reverse=True
    )[:5]

    if not entries:
        return NO_KNOWLEDGE_MESSAGE_INTEL

    entries_intel = EntriesIntel(entry_intel_list=[])

    for entry in entries:
        entries_intel.append(
            EntrySearchBot().process(user_input=user_input, entry=entry)
        )

    return KnowledgeMessageIntel(body=f'Entries: {entries_intel}', entries_intel=entries_intel)
