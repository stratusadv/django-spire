# Notification Exceptions

> **Purpose:** Provide a structured exception hierarchy for the notification system, giving processors and calling code clear, typed errors to catch and handle for each delivery channel.

---

## Why Typed Exceptions?

Rather than relying on generic Python exceptions, the notification system raises specific exceptions at each layer. This allows you to:

- Catch only the errors relevant to your code
- Distinguish between recoverable errors (e.g. a bad phone number) and unexpected failures
- Surface meaningful status messages on the `Notification` record

---

## Exception Hierarchy

All notification exceptions inherit from `DjangoSpireError`, keeping them distinct from built-in Python exceptions and easy to catch at any level.

```
DjangoSpireError
└── NotificationError
    ├── InvalidNotificationTypeError
    ├── AppNotificationError
    │   └── MissingUserError
    ├── EmailNotificationError
    └── SmsNotificationError
        └── SmsTemporaryMediaError

Exception
└── TwilioError
    ├── InvalidPhoneNumberError
    ├── TwilioResponseError
    └── TwilioAPIConcurrentError
```

---

## Core Exceptions

### `NotificationError`

Base class for all notification-related errors.

```python
from django_spire.notification.exceptions import NotificationError
```

### `InvalidNotificationTypeError`

Raised when a processor receives a `Notification` with the wrong `type`. For example, passing an `EMAIL` notification to the `AppNotificationProcessor`.

```python
from django_spire.notification.exceptions import InvalidNotificationTypeError
```

```python
try:
    AppNotificationProcessor().process(email_notification)
except InvalidNotificationTypeError as e:
    print(e)  # Expected notification type app, but received email
```

---

## App Notification Exceptions

### `AppNotificationError`

Base class for app notification errors.

```python
from django_spire.notification.app.exceptions import AppNotificationError
```

### `MissingUserError`

Raised when an `AppNotification` is processed but the linked `Notification` has no `user` assigned. App notifications require a user to determine who receives them.

```python
from django_spire.notification.app.exceptions import MissingUserError
```

```python
try:
    AppNotificationProcessor().process(notification)
except MissingUserError as e:
    print(e)  # AppNotifications must have a user associated with them
```

---

## Email Notification Exceptions

### `EmailNotificationError`

Base class for email notification errors. Raised for email-specific failures not covered by `SendGridException`.

```python
from django_spire.notification.email.exceptions import EmailNotificationError
```

---

## SMS Notification Exceptions

### `SmsNotificationError`

Base class for SMS notification errors.

```python
from django_spire.notification.sms.exceptions import SmsNotificationError
```

### `SmsTemporaryMediaError`

Raised for errors related to `SmsTemporaryMedia` records, such as accessing expired or missing media.

```python
from django_spire.notification.sms.exceptions import SmsTemporaryMediaError
```

### `TwilioError`

Base class for all Twilio API errors. These are distinct from `SmsNotificationError` — they originate from the Twilio layer rather than the notification system itself.

```python
from django_spire.notification.sms.exceptions import TwilioError
```

When the processor catches a `TwilioError`, the notification is marked as `errored` and may be retried.

### `InvalidPhoneNumberError`

Raised when the `to_phone_number` value fails format validation before the Twilio API call is made.

```python
from django_spire.notification.sms.exceptions import InvalidPhoneNumberError
```

```python
try:
    SMSNotificationProcessor().process(notification)
except InvalidPhoneNumberError as e:
    print(e)  # Invalid phone number format: 555-1234
```

### `TwilioResponseError`

Raised when the Twilio API returns an error code in its response.

```python
from django_spire.notification.sms.exceptions import TwilioResponseError
```

```python
try:
    SMSNotificationProcessor().process(notification)
except TwilioResponseError as e:
    print(e)  # Twilio Error: code=21211, message=Invalid 'To' Phone Number
```

### `TwilioAPIConcurrentError`

Raised when Twilio rejects a request due to concurrent API usage. The processor handles this automatically by reverting the notification status back to `pending` so it will be retried on the next automation run.

```python
from django_spire.notification.sms.exceptions import TwilioAPIConcurrentError
```

---

## Status Mapping

Each exception type maps to a specific `Notification` status when caught by a processor:

| Exception | Resulting Status | Retried? |
|---|---|---|
| `MissingUserError` | `errored` | Yes, via `process_errored()` |
| `InvalidNotificationTypeError` | `errored` | Yes, via `process_errored()` |
| `TwilioAPIConcurrentError` | `pending` | Yes, on next automation run |
| `TwilioError` / `TwilioResponseError` | `errored` | Yes, via `process_errored()` |
| `InvalidPhoneNumberError` | `errored` | Yes, via `process_errored()` |
| `SendGridException` | `errored` | Yes, via `process_errored()` |
| Unexpected exception | `failed` | No |
