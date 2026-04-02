# Help Desk Notifications

> **Purpose:** Automatically notify developers and managers when a new ticket is created, delivering both in-app and email notifications without any manual wiring.

---

## Why Built-in Notifications?

New support tickets need to reach the right people immediately. **The Help Desk notification system** provides:

- Automatic dispatch on ticket creation with no extra code required
- Both in-app and email notifications for developers
- In-app-only notifications for managers
- HTML-formatted email bodies with ticket details included
- Environment-aware delivery — sends to `DEVELOPMENT_EMAIL` in debug mode

---

## How It Works

When `ticket.services.create()` is called, `HelpDeskTicketNotificationService.create_new_ticket_notifications()` runs automatically. It identifies two recipient groups and creates the appropriate `Notification` and channel records for each.

The notifications are created in bulk and then processed in the background by the standard notification automations. See the [Notification Automations](../notification/automations.md) guide for setup details.

---

## Core Concepts

### Recipient Groups

| Group | How Recipients Are Identified | Channels |
|---|---|---|
| Developers | Users whose email appears in `settings.ADMINS` | App + Email |
| Managers | Users with the `delete_helpdeskticket` permission | App only |

### `HelpDeskTicketNotificationService`

Accessed on any ticket instance via `ticket.services.notification`. Called automatically by `HelpDeskTicketService.create()` — you do not need to call it directly.

```python
from django_spire.help_desk.services.notification_service import HelpDeskTicketNotificationService
```

### Notification Content

Notification content differs by channel:

**App notification body:**
```
Priority: High - Purpose: App
```

**Email notification body:** An HTML block including the ticket ID, priority, purpose, and full description.

### URL Generation

- **App notifications** use a relative URL (`/help_desk/page/<pk>/detail/`)
- **Email notifications** use an absolute URL with the current `Site` domain (`https://example.com/help_desk/page/<pk>/detail/`)

---

## Main Operations

### Triggering Notifications

Notifications fire automatically when you use the service layer to create a ticket:

```python
ticket = HelpDeskTicket()

ticket.services.create(
    created_by=request.user,
    purpose=HelpDeskTicketPurposeChoices.APP,
    priority=HelpDeskTicketPriorityChoices.HIGH,
    description='Login page throws a 500 error for SSO users.',
)
# Notifications are created here automatically — no further action needed.
```

### Settings Required

Ensure the following are configured for notifications to reach the correct recipients:

```python
# Users who receive both app and email notifications for new tickets
ADMINS = [
    ('Developer Name', 'developer@example.com'),
]

# Used as the From address for outgoing email notifications
DEFAULT_FROM_EMAIL = 'no-reply@example.com'

# In debug mode, all emails are redirected to this address instead of the real recipient
DEVELOPMENT_EMAIL = 'dev@example.com'
```

### Adding More Notification Events

The service currently supports the `NEW` ticket event type via `TicketEventType`. To add notifications for status updates or comments, extend `HelpDeskTicketNotificationService` and map the new `TicketEventType` values in `_get_ticket_event_notification_title` and `_get_ticket_event_notification_body`.
