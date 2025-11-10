from __future__ import annotations

from typing import Callable, TYPE_CHECKING

from dandy import Decoder

from django_spire.auth.controller.controller import AppAuthController
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

    if default_callable is not None:
        intent_dict['None of the above choices match the user\'s intent'] = default_callable

    return Decoder(
        mapping_keys_description='Intent of the User\'s Request',
        mapping=intent_dict
    )
