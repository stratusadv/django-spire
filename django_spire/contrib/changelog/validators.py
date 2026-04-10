from collections.abc import Sequence

from django_spire.conf import settings
from django_spire.contrib.changelog import ChangelogEntry
from django_spire.contrib.changelog.exceptions import (
    ChangeLogModuleNotFoundError,
    InvalidChangeLogInstanceError,
)
from django_spire.core.utils import get_object_from_module_string


def get_validated_changelog():
    try:
        changelog = get_object_from_module_string(
            settings.DJANGO_SPIRE_CHANGELOG_MODULE,
        )
    except ModuleNotFoundError as err:
        message = (
            'ChangeLog object not found at '
            f'{settings.DJANGO_SPIRE_CHANGELOG_MODULE}'
        )
        raise ChangeLogModuleNotFoundError(message) from err

    if not isinstance(changelog, Sequence):
        message = (
            f'ChangeLog object at {settings.DJANGO_SPIRE_CHANGELOG_MODULE} must be'
            ' a valid Sequence object'
        )
        raise InvalidChangeLogInstanceError(message)

    for entry in changelog:
        if not isinstance(entry, ChangelogEntry):
            message = (
                f'ChangeLog object at {settings.DJANGO_SPIRE_CHANGELOG_MODULE} must'
                f' only contain ChangeLogEntry objects.'
            )
            raise InvalidChangeLogInstanceError(message)

    return changelog
