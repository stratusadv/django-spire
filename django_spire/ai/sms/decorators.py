from django.http import HttpResponse, HttpResponseForbidden
import functools
from twilio import twiml
from twilio.request_validator import RequestValidator

import os


def twilio_auth_required(func):
    @functools.wraps(func)
    def decorated_function(request, *args, **kwargs):
        validator = RequestValidator(os.environ.get('TWILIO_AUTH_TOKEN'))

        request_valid = validator.validate(
            request.build_absolute_uri(),
            request.POST,
            request.META.get('HTTP_X_TWILIO_SIGNATURE', ''))

        if request_valid:
            return func(request, *args, **kwargs)
        else:
            return HttpResponseForbidden()

    return decorated_function
