from __future__ import annotations

from typing import Callable, TYPE_CHECKING

from dandy import Bot

from django_spire.conf import settings
from django_spire.core.utils import get_callable_from_module_string_and_validate_arguments

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


def generate_intent_decoder(
    request: WSGIRequest,
    default_callable: Callable | None = None
) -> Bot:
    intent_dict = {}

    if hasattr(settings, 'DJANGO_SPIRE_AI_INTENT_CHAT_ROUTERS'):
        for intent_config in settings.DJANGO_SPIRE_AI_INTENT_CHAT_ROUTERS.values():
            required_permission = intent_config.get('REQUIRED_PERMISSION')

            if required_permission and not request.user.has_perm(required_permission):
                continue

            intent_description = intent_config.get('INTENT_DESCRIPTION', '')
            chat_router_path = intent_config.get('CHAT_ROUTER')

            if chat_router_path:
                try:
                    router_class = get_callable_from_module_string_and_validate_arguments(
                        chat_router_path,
                        []
                    )

                    router_instance = router_class()

                    intent_dict[intent_description] = router_instance.workflow
                except ImportError:
                    pass

    if default_callable is not None:
        intent_dict['None of the above choices match the user\'s intent'] = default_callable

    class DecoderBot(Bot):

        def process(
                self,
                prompt,
                max_return_values: int
        ):

            return self.llm.decoder.prompt_to_values(
                prompt=prompt,
                keys_description='Intent of the User\'s Request',
                keys_values=intent_dict,
                max_return_values=max_return_values
            )

    return DecoderBot
