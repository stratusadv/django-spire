from __future__ import annotations

from typing import Any, TYPE_CHECKING

from django_spire.core.context_processors import django_spire as django_spire_default

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


# Demonstrating how to override the default django spire context processor data
def django_spire(request: WSGIRequest) -> dict[str, Any]:
    return django_spire_default(request)
