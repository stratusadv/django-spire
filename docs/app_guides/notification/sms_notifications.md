# SMS Notifications

> **Purpose:** Send SMS messages to users via Twilio's REST API, with background processing through automations, batched delivery to respect rate limits, and support for media attachments.

---

## Why SMS Notifications?

Some alerts are time-sensitive or need to reach users outside the app. **The SMS Notification system** provides:

- Twilio-powered delivery with no custom SMS infrastructure
- Background processing through automations to reduce server load
- Batched sending to stay within Twilio's rate limits
- Optional media URL support for MMS messages

---

## Quick Start

### 1. Configure Twilio Credentials

Add the following to your environment:

```
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_SMS_BATCH_SIZE=100
```

`TWILIO_SMS_BATCH_SIZE` controls how many messages are sent per batch. 100 is the recommended value.

### 2. Create the Notification

```python
from django.utils.timezone import now

from django_spire.notification.models import Notification
from django_spire.notification.choices import NotificationTypeChoices, NotificationPriorityChoices

notification = Notification.objects.create(
    user=some_user,
    type=NotificationTypeChoices.SMS,
    title='Your verification code',
    body='Your one-time code is 482910. It expires in 10 minutes.',
    priority=NotificationPriorityChoices.HIGH,
    publish_datetime=now(),
)
```

### 3. Create the SmsNotification

```python
from django_spire.notification.sms.models import SmsNotification

SmsNotification.objects.create(
    notification=notification,
    to_phone_number='+11234567890',
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
| `type` | Delivery channel — must be `NotificationTypeChoices.SMS` for SMS notifications |
| `title` | Short subject line (max 124 chars) |
| `body` | The SMS message text |
| `priority` | `low`, `medium`, or `high` |
| `status` | Lifecycle state: `pending` → `processing` → `sent` (or `errored`/`failed`) |
| `publish_datetime` | When the notification becomes eligible for sending |
| `sent_datetime` | Set automatically when processing completes |
| `content_type` / `object_id` | Optional generic FK to any related model instance |

### The `SmsNotification` Model

Extends the base `Notification` with SMS-specific delivery fields. Each `SmsNotification` has a one-to-one relationship with a `Notification`.

```python
from django_spire.notification.sms.models import SmsNotification
```

Key fields:

| Field | Description |
|---|---|
| `notification` | OneToOne link to the base `Notification` |
| `to_phone_number` | Recipient phone number (E.164 format, e.g. `+11234567890`) |
| `media_url` | Optional URL for MMS media attachment |
| `temporary_media` | Optional link to a `SmsTemporaryMedia` record for hosted media |

### The `SMSNotificationProcessor`

Handles validation and delivery when automations process notifications. It confirms the notification type is `SMS`, then sends via Twilio. If a concurrent API error occurs the notification reverts to `pending` and will be retried. Twilio errors result in `errored` status; unexpected errors result in `failed`.

### Throttling and Batch Sizes

SMS notifications are processed in batches and are designed to run on 5-minute automation intervals. This respects Twilio's rate limit of one message per second for standard accounts and a queue limit of 36,000 segments. See [Twilio's rate limit documentation](https://help.twilio.com/articles/223183648-Sending-and-Receiving-Limitations-on-Calls-and-SMS-Messages) for details.

---

## Main Operations

### Creating an SMS Notification

Always create the `Notification` first, then the `SmsNotification`:

```python
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from django.utils.timezone import now

from django_spire.notification.models import Notification
from django_spire.notification.choices import NotificationTypeChoices, NotificationPriorityChoices
from django_spire.notification.sms.models import SmsNotification

from myapp.models import Order

order = Order.objects.get(pk=1)

notification = Notification.objects.create(
    user=order.user,
    type=NotificationTypeChoices.SMS,
    title='Order shipped',
    body=f'Your order #{order.id} has shipped and is on its way!',
    priority=NotificationPriorityChoices.HIGH,
    publish_datetime=now(),
    content_type=ContentType.objects.get_for_model(order),
    object_id=order.id,
)

SmsNotification.objects.create(
    notification=notification,
    to_phone_number=order.user.profile.phone_number,
)
```

To include a media attachment (MMS), pass a `media_url`:

```python
SmsNotification.objects.create(
    notification=notification,
    to_phone_number=order.user.profile.phone_number,
    media_url='https://example.com/images/shipping-label.png',
)
```
