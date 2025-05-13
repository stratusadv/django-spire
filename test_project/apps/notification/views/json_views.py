from django.urls import reverse
from django.http import HttpResponseRedirect

from django_spire.notification.choices import NotificationTypeChoices
from django_spire.notification.email.models import EmailNotification
from django_spire.notification.email.processor import EmailNotificationProcessor
from django_spire.notification.models import Notification


def send_test_email_view(request):
    test = EmailNotification.objects.create(
        notification=Notification.objects.create(
            user=request.user,
            type=NotificationTypeChoices.EMAIL,
            title='Test Email',
            body='This is a test email',
            url='https://google.com'
        ),
        to_email_address="obrienl@stratusadv.com"
    )

    EmailNotificationProcessor().process(test.notification)
    return HttpResponseRedirect(reverse('notification:page:list'))
