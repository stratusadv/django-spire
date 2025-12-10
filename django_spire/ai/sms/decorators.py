from __future__ import annotations

import functools
import os

from typing import TYPE_CHECKING, Callable

from django.http import HttpResponseForbidden
from twilio.request_validator import RequestValidator

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest
    from django.http import HttpResponse


def twilio_auth_required(func: Callable[..., HttpResponse]) -> Callable[..., HttpResponse]:
    @functools.wraps(func)
    def decorated_function(request: WSGIRequest, *args, **kwargs) -> HttpResponse:
        request_validator = RequestValidator(os.environ.get('TWILIO_AUTH_TOKEN', ''))

        absolute_uri = request.build_absolute_uri()

        if absolute_uri[:5] == 'http:':
            absolute_uri = 'https' + absolute_uri[4:]

        request_valid = request_validator.validate(
            absolute_uri,
            request.POST,
            request.META.get('HTTP_X_TWILIO_SIGNATURE', '')
        )

        if request_valid:
            return func(request, *args, **kwargs)

        return HttpResponseForbidden()

    return decorated_function
