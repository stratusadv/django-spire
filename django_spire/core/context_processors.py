from __future__ import annotations

from typing_extensions import TYPE_CHECKING, Any

from django_spire.consts import __VERSION__
from django.urls import reverse

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


def django_spire(_: WSGIRequest) -> dict[str, Any]:
    return {
        'DJANGO_SPIRE_VERSION': __VERSION__,
        'app_bootstrap_icon': {
            'help_desk': 'bi bi-headset'
        }
    }
