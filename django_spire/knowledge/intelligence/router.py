from __future__ import annotations

from typing import TYPE_CHECKING

from django_spire.ai.chat.router import BaseChatRouter
from django_spire.knowledge.intelligence.workflows.knowledge_workflow import knowledge_search_workflow

if TYPE_CHECKING:
    from dandy.llm.request.message import MessageHistory
    from django.core.handlers.wsgi import WSGIRequest

    from django_spire.ai.chat.message_intel import BaseMessageIntel


class KnowledgeSearchRouter(BaseChatRouter):
    def workflow(
        self,
        request: WSGIRequest,
        user_input: str,
        message_history: MessageHistory | None = None
    ) -> BaseMessageIntel:
        return knowledge_search_workflow(
            request=request,
            user_input=user_input,
            message_history=message_history
        )
