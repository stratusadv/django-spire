from __future__ import annotations

from typing import TYPE_CHECKING

from django_spire.conf import settings
from django_spire.core.utils import get_callable_from_module_string_and_validate_arguments

if TYPE_CHECKING:
    from dandy.llm.request.message import MessageHistory
    from django.core.handlers.wsgi import WSGIRequest

    from django_spire.ai.chat.message_intel import BaseMessageIntel


def chat_workflow(
    request: WSGIRequest,
    user_input: str,
    message_history: MessageHistory | None = None
) -> BaseMessageIntel:
    router_key = getattr(settings, 'DJANGO_SPIRE_AI_DEFAULT_CHAT_ROUTER', 'SPIRE')

    chat_routers = getattr(settings, 'DJANGO_SPIRE_AI_CHAT_ROUTERS', {
        'SPIRE': 'django_spire.ai.chat.router.SpireChatRouter'
    })

    router_path = chat_routers.get(router_key)

    if not router_path:
        router_path = 'django_spire.ai.chat.router.SpireChatRouter'

    router_class = get_callable_from_module_string_and_validate_arguments(
        router_path,
        []
    )

    router_instance = router_class()

    return router_instance.process(
        request=request,
        user_input=user_input,
        message_history=message_history,
    )
