from __future__ import annotations

from typing import TYPE_CHECKING

from django.core.handlers.wsgi import WSGIRequest

from django_spire.ai.chat.message_intel import DefaultMessageIntel, BaseMessageIntel
from django_spire.core.tag.intelligence.tag_set_bot import TagSetBot
from django_spire.knowledge.collection.models import Collection
from django_spire.knowledge.intelligence.bots.knowledge_search_llm_bot import KnowledgeSearchBot
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

    def get_top_scored_from_dict_to_list(
            scored_dict: dict[str, float],
            score_floor: float = 0.05
    ) -> list:
        if not scored_dict:
            return []

        min_score = min(scored_dict.values())
        max_score = max(scored_dict.values())

        if min_score == 0 and max_score == 0:
            return []

        median_score = (max_score - min_score) / 2

        top_scored_list = []

        for key, value in scored_dict.items():
            if value >= score_floor and value >= median_score:
                top_scored_list.append(key)

        return top_scored_list

    collections = get_top_scored_from_dict_to_list({
        collection: collection.services.tag.get_score_percentage_from_aggregated_tag_set_weighted(
            user_tag_set
        )
        for collection in Collection.objects.all().annotate_entry_count()
    })

    entries = get_top_scored_from_dict_to_list({
        entry: entry.services.tag.get_score_percentage_from_tag_set_weighted(user_tag_set)
        for collection in collections
        for entry in collection.entries.all()
    })

    if not entries:
        return NO_KNOWLEDGE_MESSAGE_INTEL

    knowledge_answer_intel = KnowledgeSearchBot(llm_temperature=0.0).process(
        user_input=user_input,
        entries=entries
    )

    return KnowledgeMessageIntel(
        knowledge_answer_intel=knowledge_answer_intel,
    )
