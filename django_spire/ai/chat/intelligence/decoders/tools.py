from __future__ import annotations

from typing import Callable, TYPE_CHECKING

from dandy import Decoder

from django_spire.auth.controller.controller import AppAuthController
from django_spire.conf import settings
from django_spire.core.utils import get_callable_from_module_string_and_validate_arguments
from django_spire.knowledge.intelligence.workflows.knowledge_workflow import knowledge_search_workflow

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


def generate_intent_decoder(
    request: WSGIRequest,
    default_callable: Callable | None = None
) -> Decoder:
    intent_dict = {}

    if AppAuthController(app_name='knowledge', request=request).can_view():
        intent_dict['The user is looking for information or knowledge on something.'] = knowledge_search_workflow

    if settings.AI_CHAT_DEFAULT_CALLABLE is not None:
        intent_dict['None of the above choices match the user\'s intent'] = get_callable_from_module_string_and_validate_arguments(
            settings.AI_CHAT_DEFAULT_CALLABLE,
            ['request', 'user_input', 'message_history']
        )

    return Decoder(
        mapping_keys_description='Intent of the User\'s Request',
        mapping=intent_dict
    )
