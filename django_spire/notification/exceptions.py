from __future__ import annotations

from typing import TYPE_CHECKING

from django_spire.exceptions import DjangoSpireError

if TYPE_CHECKING:
    from django_spire.notification.choices import NotificationTypeChoices


class NotificationError(DjangoSpireError):
    pass


class InvalidNotificationTypeError(NotificationError):
    def __init__(self, expected_type: NotificationTypeChoices, actual_type: NotificationTypeChoices) -> None:
        super().__init__(
            f'Expected notification type {expected_type}, '
            f'but received {actual_type}'
        )
