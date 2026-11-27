from __future__ import annotations

from typing import TYPE_CHECKING

from django.conf import settings
from django.core.mail import EmailMessage

if TYPE_CHECKING:
    from django_spire.notification.models import Notification


class EmailHelper:
    def __init__(self, notification: Notification, fail_silently: bool = False) -> None:
        email = notification.email
        self.to = self._normalize_recipients(email.to) or self._normalize_recipients(email.to_email_address)
        self.cc = self._normalize_recipients(email.cc)
        self.bcc = self._normalize_recipients(email.bcc)

        self.from_email = settings.DEFAULT_FROM_EMAIL
        self.fail_silently = fail_silently

        self.attachments = []

        for attachment in list(email.attachments.all()):
            with attachment.file.open('rb') as f:
                self.attachments.append((attachment.name, f.read(), attachment.type))

    @staticmethod
    def _normalize_recipients(value: object) -> list[str]:
        if isinstance(value, str):
            return [value] if value else []

        if isinstance(value, list):
            return list(value)

        return []


class SendGridEmailHelper(EmailHelper):
    def __init__(self, notification: Notification, fail_silently: bool = False) -> None:
        super().__init__(notification, fail_silently)

        if notification.email.template_id == '':
            self.template_id = settings.SENDGRID_TEMPLATE_ID
        else:
            self.template_id = notification.email.template_id

        self.template_data = {
            'to': ', '.join(self.to),
            'from': settings.DEFAULT_FROM_EMAIL,
            'subject': notification.title,
            'body': notification.body,
            'url': notification.url,
        }

        self.template_data.update(notification.email.context_data)

    def send(self) -> None:
        msg = EmailMessage(
            from_email=self.from_email, to=self.to, cc=self.cc, bcc=self.bcc, attachments=self.attachments
        )

        msg.template_id = self.template_id
        msg.dynamic_template_data = self.template_data
        msg.send(fail_silently=self.fail_silently)
