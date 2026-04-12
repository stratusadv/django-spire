# Notification Processors

> **Purpose:** Provide a layered processing pipeline that validates, dispatches, and delivers notifications — routing each one to the correct channel processor based on its type.

---

## Why Processors?

Processors sit between the data layer (models) and delivery layer (Twilio, SendGrid, in-app). **The Processor system** provides:

- A single entry point (`NotificationProcessor`) that handles any notification type
- Channel-specific processors that validate and deliver notifications
- Consistent status lifecycle management across all channels
- Bulk processing with a single database update for efficiency

---

## Core Concepts

### `BaseNotificationProcessor`

The abstract base class all processors implement. Defines the interface every processor must follow.

```python
from django_spire.notification.processors.processor import BaseNotificationProcessor
```

Every processor implements:

| Method | Description |
|---|---|
| `process(notification)` | Process a single notification |
| `process_list(notifications)` | Process a list of notifications in bulk |
| `process_ready()` | Fetch and process all notifications ready to send |
| `process_errored()` | Fetch and retry all errored notifications |

### `NotificationProcessor`

The top-level dispatcher. Routes each notification to the correct channel processor based on `notification.type`. This is what `NotificationManager` uses under the hood.

```python
from django_spire.notification.processors.notification import NotificationProcessor
```

When processing a list, it groups notifications by type and dispatches each group to the appropriate processor in a single pass. If a notification type is unrecognised, its status is set to `failed`.

### Channel Processors

Each delivery channel has its own processor:

| Processor | Channel | Import |
|---|---|---|
| `AppNotificationProcessor` | In-app | `django_spire.notification.app.processor` |
| `EmailNotificationProcessor` | Email (SendGrid) | `django_spire.notification.email.processor` |
| `SMSNotificationProcessor` | SMS (Twilio) | `django_spire.notification.sms.processor` |

---

## Main Operations

### Processing a Single Notification

Use `NotificationProcessor` to process one notification regardless of type:

```python
from django_spire.notification.processors.notification import NotificationProcessor

notification = Notification.objects.get(pk=1)
NotificationProcessor().process(notification)
```

Or use a channel-specific processor directly when the type is known:

```python
from django_spire.notification.app.processor import AppNotificationProcessor

AppNotificationProcessor().process(notification)
```

### Processing a List of Notifications

Bulk-process a list with a single database update per channel:

```python
from django_spire.notification.processors.notification import NotificationProcessor

notifications = list(Notification.objects.ready_to_send().active())
NotificationProcessor().process_list(notifications)
```

### Processing All Ready Notifications

Each processor's `process_ready()` fetches the correct queryset and processes it:

```python
from django_spire.notification.app.processor import AppNotificationProcessor
from django_spire.notification.email.processor import EmailNotificationProcessor
from django_spire.notification.sms.processor import SMSNotificationProcessor

AppNotificationProcessor().process_ready()
EmailNotificationProcessor().process_ready()
SMSNotificationProcessor().process_ready()
```

Or process all channels at once via `NotificationProcessor`:

```python
NotificationProcessor().process_ready()
```

### Retrying Errored Notifications

```python
NotificationProcessor().process_errored()
```

Or per channel:

```python
AppNotificationProcessor().process_errored()
EmailNotificationProcessor().process_errored()
SMSNotificationProcessor().process_errored()
```

---

## Status Lifecycle

Every processor follows the same status progression:

```
pending → processing → sent
                    ↘ errored  (recoverable — retried by process_errored)
                    ↘ failed   (unexpected — not retried automatically)
```

The `processing` status is set via a bulk update before delivery begins, so interrupted jobs don't leave notifications stuck in `pending`.

---

## Using `NotificationManager` (Recommended)

For most use cases, call processors through `NotificationManager` rather than directly. It provides a stable, named API and is what the built-in automations use.

```python
from django_spire.notification.managers import NotificationManager

# Process everything
NotificationManager().process_ready_notifications()

# Process one notification
NotificationManager().process_notification(notification)

# Process a list
NotificationManager().process_notifications(notifications)
```

See the [Automations](automations.md) guide for scheduling these calls.
