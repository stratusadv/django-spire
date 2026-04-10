# Help Desk Exceptions

> **Purpose:** Provide typed exceptions for help desk errors, covering unsupported notification configurations and missing recipient data.

---

## Exception Hierarchy

```
DjangoSpireError
└── HelpDeskError
    ├── TicketEventNotificationTypeNotSupportedError  (also TypeError)
    └── HelpDeskNotificationRecipientMissingEmailError  (also ValueError)
```

---

## Exceptions

### `HelpDeskError`

Base class for all help desk errors.

```python
from django_spire.help_desk.exceptions import HelpDeskError
```

### `TicketEventNotificationTypeNotSupportedError`

Raised when a `TicketEventType` and `NotificationTypeChoices` combination has no defined content mapping, or when a notification type is used that the help desk notification service does not support at all.

```python
from django_spire.help_desk.exceptions import TicketEventNotificationTypeNotSupportedError
```

This is raised internally by `HelpDeskTicketNotificationService`. You would encounter it when extending the notification service with a new event type or notification channel that hasn't been mapped.

```python
try:
    ticket.services.notification.create_new_ticket_notifications()
except TicketEventNotificationTypeNotSupportedError as e:
    print(e)
    # "Combination of event type and notification type not supported:
    #  Event type TicketEventType.NEW - Notification type sms"
    #
    # or, when only the notification type is unknown:
    # "Notification type not supported: push"
```

### `HelpDeskNotificationRecipientMissingEmailError`

Raised when an email notification is being prepared for a recipient who has no email address on their account.

```python
from django_spire.help_desk.exceptions import HelpDeskNotificationRecipientMissingEmailError
```

```python
try:
    ticket.services.notification.create_new_ticket_notifications()
except HelpDeskNotificationRecipientMissingEmailError as e:
    print(e)  # Recipient is missing an email address: John Smith
```

---

## When These Are Raised

| Exception | Raised When |
|---|---|
| `TicketEventNotificationTypeNotSupportedError` | A notification channel or event type combination has no content mapping in the notification service |
| `HelpDeskNotificationRecipientMissingEmailError` | An email notification targets a user with no email address |
