import functools
import os

from django.http import HttpResponseForbidden
from twilio.request_validator import RequestValidator


def twilio_auth_required(func):
    @functools.wraps(func)
    def decorated_function(request, *args, **kwargs):
        request_validator = RequestValidator(os.environ.get('TWILIO_AUTH_TOKEN'))

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
        else:
            return HttpResponseForbidden()

    return decorated_function
