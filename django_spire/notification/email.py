from __future__ import annotations

from django.conf import settings
from django.core.mail import EmailMessage


class EmailHelper:
    def __init__(
        self,
        to: list | str,
        cc: list | None = None,
        bcc: list | None = None,
        fail_silently: bool = False
    ):
        if isinstance(to, str):
            self.to = [to]
        else:
            self.to = to

        self.cc = cc
        self.bcc = bcc
        self.from_email = settings.DEFAULT_FROM_EMAIL
        self.fail_silently = fail_silently


class SendGridEmailHelper(EmailHelper):
    def __init__(
        self,
        to: list | str,
        template_data: dict,
        template_id: str = settings.SENDGRID_TEMPLATE_ID,
        cc: list | None = None,
        bcc: list | None = None,
        fail_silently: bool = False
    ):
        super().__init__(to, cc, bcc, fail_silently)

        self.template_id = template_id
        self.template_data = template_data

    def send(self) -> None:
        msg = EmailMessage(
            from_email=self.from_email,
            to=self.to,
            cc=self.cc,
            bcc=self.bcc
        )
        msg.template_id = self.template_id
        msg.dynamic_template_data = self.template_data
        msg.send(fail_silently=self.fail_silently)
