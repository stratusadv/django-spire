from datetime import timedelta

from django.utils.timezone import now

from django.urls import reverse
from django.http import HttpResponseRedirect

from django_spire.notification.app.models import AppNotification
from django_spire.notification.app.processor import AppNotificationProcessor
from django_spire.notification.choices import NotificationTypeChoices
from django_spire.notification.models import Notification


def send_test_email_view(request):
    test = AppNotification.objects.create(
        notification=Notification.objects.create(
            user=request.user,
            type=NotificationTypeChoices.APP,
            title="This one is on hold",
            body="This should come out about a minute later than the other one",
            url="https://google.com",
            publish_datetime=now() + timedelta(seconds=1)
        )
    )

    testy = AppNotification.objects.create(
        notification=Notification.objects.create(
            user=request.user,
            type=NotificationTypeChoices.APP,
            title="Right now notification",
            body="The time is now!!",
            url="https://google.com",
        )
    )

    AppNotificationProcessor().process_all()

    return HttpResponseRedirect(reverse('notification:page:list'))
