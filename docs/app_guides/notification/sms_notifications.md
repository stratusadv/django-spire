# SMS Notification Guide

### 👀 Overview 
SMS Notifications in Django Spire are reliant on [Twilio's REST API](https://www.twilio.com/docs/messaging/api "Twilio SMS API Guide").

### 🎚️ Throttling and Batch Sizes
SMS notifications are processed in batches of 100 message segments and are intended to be processed in 5-minute intervals. This is because Twilio's SMS API has a limit of one message per second (for basic accounts),
and has a queue limit of 36,000 segments. ([see Twilio's documentation](https://www.twilio.com/docs/glossary/what-sms-character-limit "Twilio SMS Segments")).

See [Twilio's rate limits](https://help.twilio.com/articles/223183648-Sending-and-Receiving-Limitations-on-Calls-and-SMS-Messages "Twilio Rate Limits") for more details.

### 📱 Twilio Credentials
Twilio's credentials must be provided in the `TWILIO_ACCOUNT_SID` and `TWILIO_AUTH_TOKEN` environment variables. Additionally, the `TWILIO_SMS_BATCH_SIZE` environment variable must be set to the number of SMS messages to send per batch.
We recommend 100, as this is the maximum number of messages that can be sent per batch, but this can be changed as needed.

### Example
We must first create the `Notification` object before we create the `SmsNotification` object. Once both objects have been created, we are done! Having a automation that runs `notification.automations` will handle the rest!
For further details on the automations please see the [Automations](/app_guides/notification/automations/) guide.

```python
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse

from django.utils.timezone import now

from django_spire.notification.models import Notification
from django_spire.notification.choices import NotificationTypeChoices

from django_spire.notification.sms.models import SmsNotification

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
    type=NotificationTypeChoices.SMS,
    user=some_user,
    publish_datetime=now()
)

# Create SmsNotification
SmsNotification.objects.create(
    notification=notification,
    to_phone_number='+1234567890'
)

```
