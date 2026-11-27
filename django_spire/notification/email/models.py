from __future__ import annotations

import warnings

from typing import TYPE_CHECKING

from django.core.exceptions import ValidationError
from django.db import models

from django_spire.file.models import File
from django_spire.notification.email.querysets import EmailNotificationQuerySet
from django_spire.notification.email.validators import (
    ALL_RECIPIENT_FIELDS,
    EmailListValidator,
    MAX_EMAIL_FIELD_LENGTH,
)
from django_spire.notification.models import Notification

if TYPE_CHECKING:
    from typing_extensions import deprecated


class EmailNotification(models.Model):
    """
    It is important to note size limits for email content contained in this model. E.g., Sendgrid has a hard total email
    limit of 30mb (and a recommended limit of 10mb for attachments): https://www.twilio.com/docs/sendgrid/ui/sending-email/attachments-with-digioh#-Limitations

    .. deprecated:: 1.8.0
       ``to_email_address`` is deprecated; use ``to`` (a list of recipient email addresses) instead.
    """

    notification = models.OneToOneField(
        Notification, editable=False, on_delete=models.CASCADE, related_name='email', related_query_name='email'
    )

    attachments = models.ManyToManyField(File, blank=True, related_name='attachments', related_query_name='attachment')
    template_id = models.CharField(max_length=64, default='', blank=True)
    context_data = models.JSONField(default=dict, blank=True)

    if TYPE_CHECKING:
        @property
        @deprecated('EmailNotification.to_email_address is deprecated; use EmailNotification.to instead.')
        def to_email_address(self) -> str:
            """Deprecated: use ``to`` instead."""
            ...

        @to_email_address.setter
        @deprecated('EmailNotification.to_email_address is deprecated; use EmailNotification.to instead.')
        def to_email_address(self, value: str) -> None: ...
    else:
        to_email_address = models.EmailField(
            blank=True,
            default='',
            help_text='Deprecated: use `to` instead.',
        )
        """Deprecated: use ``to`` instead."""

    to = models.JSONField(default=list, validators=[EmailListValidator(allow_empty=False)])
    cc = models.JSONField(default=list, blank=True, validators=[EmailListValidator(allow_empty=True)])
    bcc = models.JSONField(default=list, blank=True, validators=[EmailListValidator(allow_empty=True)])

    objects = EmailNotificationQuerySet.as_manager()

    class Meta:
        db_table = 'django_spire_notification_email'
        verbose_name = 'Email Notification'
        verbose_name_plural = 'Email Notifications'

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._snapshot_recipient_fields()

    def __str__(self) -> str:
        recipients = ', '.join(self.to) if isinstance(self.to, list) else str(self.to)
        return f'{self.notification.title} - {recipients}'

    def save(self, *args, **kwargs) -> None:
        update_fields = kwargs.get('update_fields')

        if update_fields is None:
            self.sync_deprecated_to_email_address()
            self.validate_recipients()
        elif ALL_RECIPIENT_FIELDS.intersection(update_fields):
            self.sync_deprecated_to_email_address()
            self.validate_recipients()
            updated = set(update_fields)

            if 'to' in updated or 'to_email_address' in updated:
                updated.update(('to', 'to_email_address'))
                kwargs['update_fields'] = list(updated)

        super().save(*args, **kwargs)
        self._snapshot_recipient_fields()

    def clean_fields(self, exclude: set[str] | None = None) -> None:
        self.sync_deprecated_to_email_address()
        super().clean_fields(exclude=exclude)

    def clean(self) -> None:
        super().clean()
        self.sync_deprecated_to_email_address()

        if self._has_valid_recipient_lists():
            errors: dict[str, list[ValidationError]] = {}
            self._validate_unique_across_recipient_fields(errors)

            if errors:
                raise ValidationError(errors)

    def sync_deprecated_to_email_address(self) -> None:
        """Keep deprecated ``to_email_address`` and canonical ``to`` in sync."""
        deferred = self.get_deferred_fields()

        if 'to' in deferred or 'to_email_address' in deferred:
            return

        to_value = self.to
        legacy_value = self.to_email_address or ''

        to_is_empty = to_value == [] or to_value is None
        to_unchanged = self._initial_to is not None and to_value == self._initial_to
        legacy_changed = (
            self._initial_to_email_address is not None and legacy_value != self._initial_to_email_address
        )

        if to_is_empty and legacy_value:
            warnings.warn(
                'EmailNotification.to_email_address is deprecated; use EmailNotification.to=[...] instead.',
                DeprecationWarning,
                stacklevel=3,
            )
            self.to = [legacy_value]
            self._snapshot_recipient_fields()
        elif legacy_changed and to_unchanged:
            warnings.warn(
                'EmailNotification.to_email_address is deprecated; use EmailNotification.to=[...] instead.',
                DeprecationWarning,
                stacklevel=3,
            )
            self.to = [legacy_value] if legacy_value else []
            self._snapshot_recipient_fields()

        if isinstance(self.to, list) and self.to and isinstance(self.to[0], str):
            self.to_email_address = self.to[0][:MAX_EMAIL_FIELD_LENGTH]
        elif not self.to:
            self.to_email_address = ''

    def _snapshot_recipient_fields(self) -> None:
        deferred = self.get_deferred_fields()
        self._initial_to = list(self.to) if 'to' not in deferred and isinstance(self.to, list) else None
        self._initial_to_email_address = self.to_email_address if 'to_email_address' not in deferred else None

    def validate_recipients(self) -> None:
        errors: dict[str, list[ValidationError]] = {}

        field_validators = (
            ('to', self.to, EmailListValidator(allow_empty=False)),
            ('cc', self.cc, EmailListValidator(allow_empty=True)),
            ('bcc', self.bcc, EmailListValidator(allow_empty=True)),
        )

        for field_name, value, validator in field_validators:
            field_errors = self._run_recipient_validator(value, validator)

            if field_errors:
                errors[field_name] = field_errors

        if not errors:
            self._validate_unique_across_recipient_fields(errors)

        if errors:
            raise ValidationError(errors)

    def _has_valid_recipient_lists(self) -> bool:
        return all(
            isinstance(value, list) and all(isinstance(item, str) for item in value)
            for value in (self.to, self.cc, self.bcc)
        )

    @staticmethod
    def _run_recipient_validator(value: object, validator: EmailListValidator) -> list[ValidationError]:
        try:
            validator(value)
        except ValidationError as exc:
            return exc.error_list

        return []

    def _validate_unique_across_recipient_fields(self, errors: dict[str, list[ValidationError]]) -> None:
        seen_emails: set[str] = {email.lower() for email in self.to}
        duplicate_message = 'Duplicate recipient across to, cc, and bcc: %(value)s.'

        for field_name, recipients in (('cc', self.cc), ('bcc', self.bcc)):
            duplicates = [email for email in recipients if email.lower() in seen_emails]

            if duplicates:
                errors[field_name] = [
                    ValidationError(duplicate_message, code='duplicate_recipient', params={'value': email})
                    for email in duplicates
                ]

            seen_emails.update(email.lower() for email in recipients)
