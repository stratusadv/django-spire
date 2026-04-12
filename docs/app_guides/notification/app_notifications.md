# App Notifications

> **Purpose:** Deliver in-app notifications to users entirely within your Django application — no third-party service required — with support for custom templates, priority levels, and background processing via automations.

---

## Why App Notifications?

Many applications need to surface messages to users without leaving the app. **The App Notification system** provides:

- Local delivery with no external service dependencies
- Background processing through automations to reduce server load
- Custom templates and context data for flexible rendering
- Priority levels to control display order
- Viewed tracking per user
- Queryset helpers for filtering, searching, and serialization

---

## Quick Start

### 1. Create the Notification

```python
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from django.utils.timezone import now

from django_spire.notification.models import Notification
from django_spire.notification.choices import NotificationTypeChoices, NotificationPriorityChoices

from myapp.models import Order

order = Order.objects.get(pk=1)

notification = Notification.objects.create(
    user=order.user,
    type=NotificationTypeChoices.APP,
    title='Your order has shipped!',
    body='Order #1234 is on its way.',
    url=reverse('orders:detail', kwargs={'pk': order.id}),
    priority=NotificationPriorityChoices.HIGH,
    publish_datetime=now(),
    content_type=ContentType.objects.get_for_model(order),
    object_id=order.id,
)
```

### 2. Create the AppNotification

```python
from django_spire.notification.app.models import AppNotification

AppNotification.objects.create(
    notification=notification,
    template='django_spire/notification/app/item/notification_item.html',
    context_data={
        'tracking_number': 'ABC123',
    }
)
```

### 3. Let Automations Handle Processing

Once both objects exist, an automation calling `notification.automations` will pick up and process the notification in the background. See the [Automations](automations.md) guide for setup details.

---

## Core Concepts

### The `Notification` Model

The base record for every notification in the system. It holds the content, delivery metadata, and links to the target user and optional related object.

```python
from django_spire.notification.models import Notification
```

Key fields:

| Field | Description |
|---|---|
| `user` | The recipient (`User` FK, optional) |
| `type` | Delivery channel — must be `NotificationTypeChoices.APP` for app notifications |
| `title` | Short subject line (max 124 chars) |
| `body` | Full message text |
| `url` | Optional link URL for the notification |
| `priority` | `low`, `medium`, or `high` |
| `status` | Lifecycle state: `pending` → `processing` → `sent` (or `errored`/`failed`) |
| `publish_datetime` | When the notification becomes eligible for sending |
| `sent_datetime` | Set automatically when processing completes |
| `content_type` / `object_id` | Optional generic FK to any related model instance |

### The `AppNotification` Model

Extends the base `Notification` with app-specific fields. Each `AppNotification` has a one-to-one relationship with a `Notification`.

```python
from django_spire.notification.app.models import AppNotification
```

Key fields:

| Field | Description |
|---|---|
| `notification` | OneToOne link to the base `Notification` |
| `template` | Template path used to render this notification in the UI |
| `context_data` | JSON dict of extra variables passed to the template |

The default template is `django_spire/notification/app/item/notification_item.html`.

### The `AppNotificationProcessor`

Handles validation and status updates when automations process notifications. It confirms the notification type is `APP` and that a user is assigned, then marks the notification as `sent`.

---

## Main Operations

### Creating an App Notification

Always create the `Notification` first, then the `AppNotification`:

```python
from django.utils.timezone import now

from django_spire.notification.models import Notification
from django_spire.notification.choices import NotificationTypeChoices, NotificationPriorityChoices
from django_spire.notification.app.models import AppNotification

notification = Notification.objects.create(
    user=some_user,
    type=NotificationTypeChoices.APP,
    title='Welcome to the platform!',
    body='Thanks for signing up. Here is how to get started.',
    priority=NotificationPriorityChoices.MEDIUM,
    publish_datetime=now(),
)

AppNotification.objects.create(
    notification=notification,
)
```

Pass `context_data` to make extra variables available in the template:

```python
AppNotification.objects.create(
    notification=notification,
    template='myapp/notifications/welcome.html',
    context_data={
        'first_name': some_user.first_name,
        'dashboard_url': '/dashboard/',
    }
)
```

In your template, access these variables directly — for example, `{ notification.context_data.first_name }`.

### Querying Notifications for a User

```python
from django_spire.notification.app.models import AppNotification

# All sent notifications for a user
notifications = AppNotification.objects.by_user(user).is_sent()

# Only unread notifications
unread = AppNotification.objects.exclude_viewed_by_user(user)

# Ordered by priority then recency
ordered = AppNotification.objects.by_user(user).is_sent().ordered_by_priority_and_sent_datetime()
```

### Filtering and Searching

```python
# Search by title or body
results = AppNotification.objects.by_user(user).search('shipment')

# Filter by priority
results = AppNotification.objects.bulk_filter({'priority': 'high'})

# Combine search and priority filter
results = AppNotification.objects.bulk_filter({
    'priority': 'high',
    'search': 'order',
})
```

### Serializing a Notification

```python
app_notification = AppNotification.objects.get(pk=1)

# As a Python dict
data = app_notification.as_dict()

# As a JSON string
json_str = app_notification.as_json()
```

`as_dict()` returns: `id`, `title`, `body`, `context_data`, `priority`, `url`, `time_since_delivered`.

