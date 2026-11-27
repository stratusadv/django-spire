from __future__ import annotations

import pytest

from django.core.exceptions import ValidationError

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.notification.email.validators import EmailListValidator


class EmailListValidatorTests(BaseTestCase):
    def test_accepts_single_and_multiple_valid_emails(self):
        validator = EmailListValidator(allow_empty=False)
        validator(['user@example.com'])
        validator(['first@example.com', 'second@example.com'])

    def test_accepts_empty_list_when_allowed(self):
        validator = EmailListValidator(allow_empty=True)
        validator([])

    def test_rejects_empty_list_when_disallowed(self):
        validator = EmailListValidator(allow_empty=False)

        with pytest.raises(ValidationError) as exc_info:
            validator([])

        assert exc_info.value.code == 'empty'

    def test_rejects_non_list_values(self):
        validator = EmailListValidator()

        for invalid_value in ('user@example.com', {'email': 'user@example.com'}, 123, None, ('user@example.com',)):
            with pytest.raises(ValidationError) as exc_info:
                validator(invalid_value)

            assert exc_info.value.code == 'invalid_type'

    def test_rejects_non_string_entries(self):
        validator = EmailListValidator()

        for invalid_list in ([123], [None], [['user@example.com']]):
            with pytest.raises(ValidationError):
                validator(invalid_list)

    def test_rejects_blank_and_whitespace_padded_emails(self):
        validator = EmailListValidator()

        for invalid_list in ([''], ['   '], [' user@example.com'], ['user@example.com ']):
            with pytest.raises(ValidationError):
                validator(invalid_list)

    def test_rejects_invalid_email_addresses(self):
        validator = EmailListValidator()

        for invalid_list in (['not-an-email'], ['user@'], ['@example.com'], ['valid@example.com', 'invalid-email']):
            with pytest.raises(ValidationError):
                validator(invalid_list)

    def test_rejects_duplicate_emails_case_insensitively(self):
        validator = EmailListValidator()

        with pytest.raises(ValidationError) as exc_info:
            validator(['User@example.com', 'user@example.com'])

        assert exc_info.value.error_list[0].code == 'duplicate_email'

    def test_deconstruct_and_equality(self):
        strict = EmailListValidator(allow_empty=False)
        optional = EmailListValidator(allow_empty=True)

        assert strict == EmailListValidator(allow_empty=False)
        assert strict != optional
        assert strict != 'not-a-validator'

        path, args, kwargs = strict.deconstruct()
        assert path == 'django_spire.notification.email.validators.EmailListValidator'
        assert args == ()
        assert kwargs == {'allow_empty': False}
