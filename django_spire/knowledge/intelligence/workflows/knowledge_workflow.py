from __future__ import annotations

from typing import TYPE_CHECKING

from django.db.models import Prefetch

from django_spire.ai.chat.message_intel import BaseMessageIntel, DefaultMessageIntel
from django_spire.knowledge.entry.models import Entry
from django_spire.knowledge.intelligence.bots.knowledge_answer_bot import KnowledgeAnswerBot
from django_spire.knowledge.intelligence.bots.knowledge_entries_bot import KnowledgeEntriesBot
from django_spire.knowledge.intelligence.intel.message_intel import KnowledgeMessageIntel

if TYPE_CHECKING:
    from dandy.llm.request.message import MessageHistory
    from django.core.handlers.wsgi import WSGIRequest


NO_KNOWLEDGE_MESSAGE_INTEL = DefaultMessageIntel(
    text='Sorry, I could not find any information on that.'
)


def knowledge_search_workflow(
    request: WSGIRequest,
    user_input: str,
    message_history: MessageHistory | None = None,
    max_results: int = 10,
    use_llm_preprocessing: bool = True,
) -> BaseMessageIntel | None:
    from django_spire.knowledge.entry.version.block.models import EntryVersionBlock

    entries = list(
        Entry.services.search
        .search(
            query=user_input,
            use_llm_preprocessing=use_llm_preprocessing,
        )
        .user_has_access(user=request.user)
        .select_related('current_version', 'current_version__author', 'collection')
        .prefetch_related(
            Prefetch(
                'current_version__blocks',
                queryset=EntryVersionBlock.objects.active().order_by('order')
            )
        )[:max_results]
    )

    if not entries:
        return NO_KNOWLEDGE_MESSAGE_INTEL

    answer_intel_future = KnowledgeAnswerBot(llm_temperature=0.5).process_to_future(
        user_input=user_input,
        entries=entries,
        message_history=message_history,
    )

    entries_intel_future = KnowledgeEntriesBot(llm_temperature=0.5).process_to_future(
        user_input=user_input,
        entries=entries
    )

    return KnowledgeMessageIntel(
        answer_intel=answer_intel_future.result,
        entries_intel=entries_intel_future.result,
    )
