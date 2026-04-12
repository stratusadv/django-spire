# Email Notifications

> **Purpose:** Send transactional emails to users via SendGrid, with support for dynamic templates, context data, attachments, CC/BCC recipients, and background processing through automations.

---

## Why Email Notifications?

Email is the most common channel for transactional messaging. **The Email Notification system** provides:

- SendGrid-powered delivery with no custom mail server setup
- Dynamic template support via SendGrid template IDs
- Context data for populating template variables
- File attachments, CC, and BCC recipient support
- Background processing through automations to reduce server load

---

## Quick Start

### 1. Configure SendGrid Credentials

Add the following to your `settings.py`:

```python
SENDGRID_API_KEY = 'your_api_key'
DEFAULT_FROM_EMAIL = 'no-reply@example.com'
SENDGRID_TEMPLATE_ID = 'your_default_template_id'
SENDGRID_SANDBOX_MODE_IN_DEBUG = True  # Set False in production
SERVER_EMAIL = 'server@example.com'
EMAIL_BACKEND = 'sendgrid_backend.SendgridBackend'
```

### 2. Create the Notification

```python
from django.utils.timezone import now

from django_spire.notification.models import Notification
from django_spire.notification.choices import NotificationTypeChoices, NotificationPriorityChoices

notification = Notification.objects.create(
    user=some_user,
    type=NotificationTypeChoices.EMAIL,
    title='Welcome to the platform!',
    body='Thanks for signing up. Here is how to get started.',
    priority=NotificationPriorityChoices.MEDIUM,
    publish_datetime=now(),
)
```

### 3. Create the EmailNotification

```python
from django_spire.notification.email.models import EmailNotification

EmailNotification.objects.create(
    notification=notification,
    to_email_address='user@example.com',
)
```

### 4. Let Automations Handle Processing

Once both objects exist, an automation calling `notification.automations` will process the notification in the background. See the [Automations](automations.md) guide for setup details.

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
| `type` | Delivery channel — must be `NotificationTypeChoices.EMAIL` for email notifications |
| `title` | Email subject line (max 124 chars) |
| `body` | Fallback message text |
| `priority` | `low`, `medium`, or `high` |
| `status` | Lifecycle state: `pending` → `processing` → `sent` (or `errored`/`failed`) |
| `publish_datetime` | When the notification becomes eligible for sending |
| `sent_datetime` | Set automatically when processing completes |
| `content_type` / `object_id` | Optional generic FK to any related model instance |

### The `EmailNotification` Model

Extends the base `Notification` with email-specific delivery fields. Each `EmailNotification` has a one-to-one relationship with a `Notification`.

```python
from django_spire.notification.email.models import EmailNotification
```

Key fields:

| Field | Description |
|---|---|
| `notification` | OneToOne link to the base `Notification` |
| `to_email_address` | Recipient email address |
| `template_id` | SendGrid template ID — overrides the default `SENDGRID_TEMPLATE_ID` |
| `context_data` | JSON dict of variables passed to the SendGrid template |
| `cc` | JSON list of CC email addresses |
| `bcc` | JSON list of BCC email addresses |
| `attachments` | M2M to `File` records included as email attachments |

> **Note:** SendGrid has a hard total email size limit of 30MB. Keep attachments under 10MB each where possible.

### The `EmailNotificationProcessor`

Handles validation and delivery when automations process notifications. It confirms the notification type is `EMAIL`, then sends via SendGrid. SendGrid errors result in `errored` status; unexpected errors result in `failed`.

---

## Main Operations

### Creating an Email Notification

Always create the `Notification` first, then the `EmailNotification`:

```python
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from django.utils.timezone import now

from django_spire.notification.models import Notification
from django_spire.notification.choices import NotificationTypeChoices, NotificationPriorityChoices
from django_spire.notification.email.models import EmailNotification

from myapp.models import Order

order = Order.objects.get(pk=1)

notification = Notification.objects.create(
    user=order.user,
    type=NotificationTypeChoices.EMAIL,
    title='Your order has shipped!',
    body=f'Order #{order.id} is on its way.',
    priority=NotificationPriorityChoices.HIGH,
    publish_datetime=now(),
    content_type=ContentType.objects.get_for_model(order),
    object_id=order.id,
)

EmailNotification.objects.create(
    notification=notification,
    to_email_address=order.user.email,
    context_data={
        'order_id': order.id,
        'tracking_number': 'ABC123',
    },
)
```

### Adding CC, BCC, and Attachments

```python
from django_spire.file.models import File

invoice = File.objects.get(pk=1)

email_notification = EmailNotification.objects.create(
    notification=notification,
    to_email_address=order.user.email,
    cc=['manager@example.com'],
    bcc=['audit@example.com'],
)

email_notification.attachments.add(invoice)
```

### Using a Custom Template

Pass a `template_id` to override the default SendGrid template for this notification:

```python
EmailNotification.objects.create(
    notification=notification,
    to_email_address=order.user.email,
    template_id='d-abc123customtemplateid',
    context_data={
        'first_name': order.user.first_name,
    },
)
```
