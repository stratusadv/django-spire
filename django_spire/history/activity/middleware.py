from __future__ import annotations

from typing import TYPE_CHECKING

from django_spire.history.activity.context import reset_current_user, set_current_user

if TYPE_CHECKING:
    from collections.abc import Callable

    from django.http import HttpRequest, HttpResponse


class ActivityUserMiddleware:
    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        token = set_current_user(getattr(request, 'user', None))

        try:
            response = self.get_response(request)
        finally:
            reset_current_user(token)

        return response
