from __future__ import annotations

from typing import TYPE_CHECKING

from django_spire.exceptions import DjangoSpireError

if TYPE_CHECKING:
    from django_spire.help_desk.enums import TicketEventType
    from django_spire.notification.choices import NotificationTypeChoices


class HelpDeskError(DjangoSpireError):
    pass


class TicketEventNotificationTypeNotSupportedError(HelpDeskError, TypeError):
    def __init__(
        self,
        event_type: TicketEventType | None,
        notification_type: NotificationTypeChoices
    ) -> None:
        if event_type is None:
            super().__init__(f'Notification type not supported: {notification_type}')
        else:
            super().__init__(
                f'Combination of event type and notification type not supported: '
                f'Event type {event_type} - Notification type {notification_type}'
            )


class HelpDeskNotificationRecipientMissingEmailError(HelpDeskError, ValueError):
    def __init__(self, recipient: str) -> None:
        super().__init__(f'Recipient is missing an email address: {recipient}')
