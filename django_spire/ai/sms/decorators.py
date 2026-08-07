from __future__ import annotations

import functools
import logging
import os

from typing import TYPE_CHECKING, Callable

from django.http import HttpResponseForbidden
from twilio.request_validator import RequestValidator

from django_spire.conf import settings

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest
    from django.http import HttpResponse


log = logging.getLogger(__name__)


def twilio_auth_required(func: Callable[..., HttpResponse]) -> Callable[..., HttpResponse]:
    @functools.wraps(func)
    def decorated_function(request: WSGIRequest, *args, **kwargs) -> HttpResponse:
        auth_token = settings.TWILIO_AUTH_TOKEN or os.environ.get('TWILIO_AUTH_TOKEN')

        if not auth_token:
            log.error('TWILIO_AUTH_TOKEN is not configured; rejecting webhook request')
            return HttpResponseForbidden()

        request_validator = RequestValidator(auth_token)

        absolute_uri = request.build_absolute_uri().replace('http:', 'https:', 1)

        request_valid = request_validator.validate(
            absolute_uri,
            request.POST,
            request.META.get('HTTP_X_TWILIO_SIGNATURE', ''),
        )

        if request_valid:
            return func(request, *args, **kwargs)

        return HttpResponseForbidden()

    return decorated_function
