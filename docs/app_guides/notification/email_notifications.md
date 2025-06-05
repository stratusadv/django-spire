# Email Notification Guide

### 👀 Overview 
Email Notifications in Django Spire are reliant on See the [SendGrid Django Guide](https://www.twilio.com/docs/sendgrid/for-developers/sending-email/django).

### 📱 Sendgrid Credentials
The following credentials must be provided in `settings.py`:

- `SENDGRID_API_KEY`
- `DEFAULT_FROM_EMAIL`
- `SENDGRID_TEMPLATE_ID`
- `SENDGRID_SANDBOX_MODE_IN_DEBUG`
- `SERVER_EMAIL`
- `EMAIL_BACKEND`

### Example
We must first create the `Notification` object before we create the `EmailNotification` object. Once both objects have been created, we are done! Having a automation that runs `notification.automations` will handle the rest!
For further details on the automations please see the [Automations](automations.md) guide.

```python
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse

from django.utils.timezone import now

from django_spire.notification.models import Notification
from django_spire.notification.choices import NotificationTypeChoices

from django_spire.notification.email.models import EmailNotification

from foo.models import Foo # import your models here

foo = Foo.objects.get(...)

# Create Notification Object
notification = Notification.objects.create(
    content_type=ContentType.objects.get_for_model(foo),
    object_id=foo.id,
    title='This Notification is About Foo!',
    body='Foo is a very good name when trying to abstract out specific'
         ' logic that is not needed to solve the problem at hand.',
    url=reverse(
        'foo:page:detail',
        kwargs={'pk': foo.id}
    ),
    type=NotificationTypeChoices.EMAIL,
    user=some_user,
    publish_datetime=now()
)

# Create SmsNotification
EmailNotification.objects.create(
    notification=notification,
    to_email_address='test@example.com'
)

```
