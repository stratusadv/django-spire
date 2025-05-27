from __future__ import annotations

from django.conf import settings
from django.core.mail import EmailMessage

from django_spire.notification.models import Notification


class EmailHelper:
    def __init__(self, notification: Notification, fail_silently: bool = False):
        if isinstance(notification.email.to_email_address, str):
            self.to = [notification.email.to_email_address]
        else:
            self.to = notification.email.to_email_address

        # self.cc = notification.email.cc
        # self.bcc = notification.email.bcc
        self.from_email = settings.DEFAULT_FROM_EMAIL
        self.fail_silently = fail_silently


class SendGridEmailHelper(EmailHelper):
    def __init__(
        self,
        notification: Notification,
        fail_silently: bool = False
    ):
        super().__init__(notification, fail_silently)

        if notification.email.template_id == '':
            self.template_id = settings.SENDGRID_TEMPLATE_ID

        else:
            self.template_id = notification.email.template_id

        self.template_data = {
            'to': notification.email.to_email_address,
            'from': settings.DEFAULT_FROM_EMAIL,
            'subject': notification.title,
            'body': notification.body,
            'link': notification.url
        }

        print(self.template_data)

    def send(self) -> None:
        msg = EmailMessage(
            from_email=self.from_email,
            to=self.to,
            # cc=self.cc,
            # bcc=self.bcc,
            cc=None,
            bcc=None,
        )
        msg.template_id = self.template_id
        msg.dynamic_template_data = self.template_data
        msg.send(fail_silently=self.fail_silently)
