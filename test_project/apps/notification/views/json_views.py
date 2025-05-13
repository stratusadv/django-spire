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
            title="Test App Notification",
            body="This is a test app notification",
            url="https://google.com",
        )
    )

    testy = AppNotification.objects.create(
        notification=Notification.objects.create(
            user=request.user,
            type=NotificationTypeChoices.APP,
            title="Test App Notification 2",
            body="This is a test app notification 2",
            url="https://google.com",
        )
    )

    # AppNotificationProcessor().process_list([test.notification, testy.notification])
    return HttpResponseRedirect(reverse('notification:page:list'))
