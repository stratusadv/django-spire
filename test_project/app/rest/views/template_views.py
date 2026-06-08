from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


def list_items_view(request: WSGIRequest) -> None:
    pass
