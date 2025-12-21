from __future__ import annotations

from django_spire.exceptions import DjangoSpireError


class AppNotificationError(DjangoSpireError):
    pass


class MissingUserError(AppNotificationError):
    def __init__(self) -> None:
        super().__init__('AppNotifications must have a user associated with them')
