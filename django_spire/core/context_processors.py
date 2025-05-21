from __future__ import annotations

from typing_extensions import TYPE_CHECKING, Any

from django_spire.consts import __VERSION__

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


def django_spire(_: WSGIRequest) -> dict[str, Any]:
    return {
        'DJANGO_SPIRE_VERSION': __VERSION__,
        'app_bootstrap_icon': {
            'ai': 'ai_icon_string',
            'ai_chat': 'chat_icon_string',
            'help_desk': 'help_desk_icon_string',
            'other': 'something'
        }
    }
