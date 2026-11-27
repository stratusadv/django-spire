from __future__ import annotations

from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.utils.deconstruct import deconstructible


RECIPIENT_FIELDS = frozenset({'to', 'cc', 'bcc'})
ALL_RECIPIENT_FIELDS = frozenset({'to', 'to_email_address', 'cc', 'bcc'})
MAX_EMAIL_FIELD_LENGTH = 254


@deconstructible
class EmailListValidator:
    def __init__(self, allow_empty: bool = True) -> None:
        self.allow_empty = allow_empty

    def __call__(self, value: object) -> None:
        if not isinstance(value, list):
            message = 'Value must be a list of email addresses.'
            raise ValidationError(message, code='invalid_type')

        if not self.allow_empty and len(value) == 0:
            message = 'At least one email address is required.'
            raise ValidationError(message, code='empty')

        errors: list[ValidationError] = []
        seen_emails: set[str] = set()

        for entry in value:
            error = self._validate_entry(entry, seen_emails)

            if error is not None:
                errors.append(error)

        if errors:
            raise ValidationError(errors)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, EmailListValidator) and self.allow_empty == other.allow_empty

    def __hash__(self) -> int:
        return hash((self.__class__, self.allow_empty))

    @staticmethod
    def _validate_entry(entry: object, seen_emails: set[str]) -> ValidationError | None:
        if not isinstance(entry, str) or not entry or entry != entry.strip():
            message = '%(value)r is not a valid email address.'
            return ValidationError(message, code='invalid_email', params={'value': entry})

        try:
            validate_email(entry)
        except ValidationError:
            message = '%(value)r is not a valid email address.'
            return ValidationError(message, code='invalid_email', params={'value': entry})

        normalized = entry.lower()

        if normalized in seen_emails:
            message = 'Duplicate email address: %(value)s.'
            return ValidationError(message, code='duplicate_email', params={'value': entry})

        seen_emails.add(normalized)
        return None
