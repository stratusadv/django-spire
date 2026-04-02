# Notification Automations

> **Purpose:** Schedule recurring background jobs that process pending notifications and clean up expired SMS media, keeping the notification pipeline running without manual intervention.

---

## Why Automations?

Notification processing is intentionally decoupled from request handling to keep response times fast. **Automations** are the scheduled jobs that close that gap by:

- Periodically picking up all pending notifications and dispatching them
- Retrying notifications that previously errored
- Cleaning up expired SMS temporary media
- Running independently of web traffic so processing load doesn't affect users

---

## Quick Start

### 1. Register the Automation

Add the built-in `process_notifications` function to your Robit scheduler:

```python
from django_spire.notification import automations as notification_automations

wo.add_group('Notifications')

wo.add_job(
    name='Process Ready Notifications',
    method=notification_automations.process_notifications,
    group='Notifications',
    cron='30 */5 * * * *',
)
```

This single job processes all pending notifications across every channel (app, email, SMS) on a 5-minute interval.

### 2. That's It

Once registered, the automation calls `NotificationManager().process_ready_notifications()` on each run, which routes each pending notification to the correct channel processor automatically.

---

## Core Concepts

### The `process_notifications` Function

The ready-to-use automation entry point. It calls `NotificationManager().process_ready_notifications()` and is decorated with `@close_db_connections` to safely release database connections after each run.

```python
from django_spire.notification.automations import process_notifications
```

### The `NotificationManager`

The `NotificationManager` is the high-level coordinator for all notification processing. It delegates to the appropriate channel processor (`AppNotificationProcessor`, `EmailNotificationProcessor`, `SMSNotificationProcessor`) based on the notification type.

```python
from django_spire.notification.managers import NotificationManager
```

### SMS Temporary Media Cleanup

SMS notifications that use hosted media (MMS) reference `SmsTemporaryMedia` records. A separate automation clears these records once they have expired or all associated notifications have been sent.

```python
from django_spire.notification.sms.automations import clear_sms_temporary_media
```

---

## Main Operations

### Process All Ready Notifications

The standard automation — processes all pending notifications across every channel:

```python
from django_spire.notification.managers import NotificationManager

NotificationManager().process_ready_notifications()
```

### Process by Channel

To process a single channel independently:

```python
NotificationManager().process_ready_app_notifications()
NotificationManager().process_ready_email_notifications()
NotificationManager().process_ready_sms_notifications()
```

This is useful when channels have different schedules. For example, SMS notifications should run on 5-minute intervals due to Twilio's rate limits, while app notifications can run more frequently.

### Retry Errored Notifications

To retry notifications that previously failed with an `errored` status:

```python
NotificationManager().process_errored_notifications()      # All channels
NotificationManager().process_errored_app_notifications()
NotificationManager().process_errored_email_notifications()
NotificationManager().process_errored_sms_notifications()
```

### Clean Up SMS Temporary Media

Register the SMS media cleanup as a separate job to run periodically:

```python
from django_spire.notification.sms import automations as sms_automations

wo.add_job(
    name='Clear SMS Temporary Media',
    method=sms_automations.clear_sms_temporary_media,
    group='Notifications',
    cron='0 */1 * * * *',
)
```

---

## Scheduling Recommendations

| Job | Recommended Interval | Reason |
|---|---|---|
| `process_notifications` | Every 5 minutes | Balances delivery speed with Twilio's SMS rate limits |
| `process_errored_notifications` | Every 15–30 minutes | Avoids hammering failing services on retry |
| `clear_sms_temporary_media` | Every hour | Keeps the media table clean without excessive overhead |
