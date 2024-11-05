from __future__ import annotations

from typing_extensions import TYPE_CHECKING

from django.utils import timezone
from datetime import datetime, timedelta

from django_spire.user_account.factories import get_or_create_user_profile

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


class UserSettingsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: WSGIRequest):
        """
            Activates the user's timezone and updates the user's settings in the session every 5 minutes.
        """
        if request.user.is_authenticated:
            profile = get_or_create_user_profile(request.user)
            last_update = request.session.get('user_options_expiry_time')

            if last_update is not None:
                last_update = datetime.fromtimestamp(last_update)

            if last_update is None or datetime.now() - last_update >= timedelta(minutes=5):
                request.session['user_options'] = profile.options.to_dict()
                request.session['user_options_expiry_time'] = datetime.now().timestamp()

            timezone.activate(profile.get_option('system', 'timezone'))

        return self.get_response(request)
