# SMS Notification Guide

### 👀 Overview 
The built in notification automation is meant to process any `Notifications` that are pending, when ran on an automation schedule.
The automation will process any `Notifications` that are ready to be processed by default. Of course, create your own automations as you see fit.
We have provided several basic processors and utilities to help you get started, and should cover most general use cases.

```python
from __future__ import annotations

from django_spire.notification.managers import NotificationManager


def process_notifications() -> str:
    NotificationManager().process_ready_notifications()

    return 'Successfully Completed'

```

See the [Notification Processor](https://github.com/stratusadv/django-spire/blob/main/django_spire/notification/processors/notification.py)
or the [Notification Manager](https://github.com/stratusadv/django-spire/blob/main/django_spire/notification/processors/notification.py)
for more information.

### Example
See the following `Robit` automation for implementation.
```python
from django_spire.notification import automations as notification_automations

wo.add_group('Notifications')

wo.add_job(
    name="Process Ready Notifications",
    method=notification_automations.process_notifications,
    group='Notifications',
    cron='30 */5 * * * *'
)
```

It really is as simple as that!
