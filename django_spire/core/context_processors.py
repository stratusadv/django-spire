from __future__ import annotations

from typing_extensions import TYPE_CHECKING

from django_spire.consts import __VERSION__

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


def spire(_: WSGIRequest) -> dict[str, str]:
    return {'DJANGO_SPIRE_VERSION': __VERSION__}
