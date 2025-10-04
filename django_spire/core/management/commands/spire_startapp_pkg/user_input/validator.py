from __future__ import annotations

from pathlib import Path

from django.conf import settings
from django.core.management.base import CommandError


class UserInputValidator:
    def check_app_exists(self, components: list[str]) -> None:
        destination = Path(settings.BASE_DIR).joinpath(*components)

        if destination.exists() and any(destination.iterdir()):
            message = (
                f'\nThe app already exists at {destination}. '
                'Please remove the existing app or choose a different name.'
            )

            raise CommandError(message)

