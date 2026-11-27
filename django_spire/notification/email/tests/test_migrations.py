from __future__ import annotations

import importlib

from types import SimpleNamespace
from unittest.mock import MagicMock

from django_spire.core.tests.test_cases import BaseTestCase


migration_module = importlib.import_module(
    'django_spire.notification.email.migrations.0004_emailnotification_to_and_more'
)


def _build_fake_apps(rows: list[SimpleNamespace]) -> tuple[MagicMock, MagicMock]:
    fake_manager = MagicMock()
    fake_manager.iterator.return_value = iter(rows)
    fake_model = MagicMock()
    fake_model.objects = fake_manager
    fake_apps = MagicMock()
    fake_apps.get_model.return_value = fake_model
    return fake_apps, fake_manager


class EmailNotificationMigration0004Tests(BaseTestCase):
    def test_parse_recipient_string_variants(self):
        parse = migration_module._parse_recipient_string

        assert parse('user@example.com') == ['user@example.com']
        assert parse('  user@example.com  ') == ['user@example.com']
        assert parse('') == []
        assert parse('   ') == []
        assert parse('a@example.com, b@example.com; c@example.com') == [
            'a@example.com',
            'b@example.com',
            'c@example.com',
        ]
        assert parse("['a@example.com', 'b@example.com']") == ['a@example.com', 'b@example.com']
        assert parse('["a@example.com", " b@example.com "]') == ['a@example.com', 'b@example.com']

    def test_migrate_email_recipients_normalizes_and_deduplicates(self):
        rows = [
            SimpleNamespace(pk=1, to_email_address='single@example.com', to=[], cc={}, bcc='bcc@example.com'),
            SimpleNamespace(
                pk=2,
                to_email_address='a@example.com, A@example.com, b@example.com',
                to=[],
                cc=['B@example.com', 'cc@example.com', ' '],
                bcc=['CC@example.com', 'bcc@example.com'],
            ),
            SimpleNamespace(pk=3, to_email_address='   ', to=[], cc=None, bcc=[]),
        ]
        fake_apps, fake_manager = _build_fake_apps(rows)

        migration_module.migrate_email_recipients(fake_apps, None)

        assert rows[0].to == ['single@example.com']
        assert rows[0].to_email_address == 'single@example.com'
        assert rows[0].cc == []
        assert rows[0].bcc == ['bcc@example.com']

        assert rows[1].to == ['a@example.com', 'b@example.com']
        assert rows[1].to_email_address == 'a@example.com'
        assert rows[1].cc == ['cc@example.com']
        assert rows[1].bcc == ['bcc@example.com']

        assert rows[2].to == []
        assert rows[2].to_email_address == ''
        assert rows[2].cc == []
        assert rows[2].bcc == []

        fake_manager.bulk_update.assert_called_once_with(rows, ['to', 'to_email_address', 'cc', 'bcc'])

    def test_revert_email_recipients(self):
        rows = [
            SimpleNamespace(pk=1, to=['first@example.com', 'second@example.com'], to_email_address=''),
            SimpleNamespace(pk=2, to=[], to_email_address=''),
        ]
        fake_apps, fake_manager = _build_fake_apps(rows)

        migration_module.revert_email_recipients(fake_apps, None)

        assert rows[0].to_email_address == 'first@example.com'
        assert rows[1].to_email_address == ''
        fake_manager.bulk_update.assert_called_once_with(rows, ['to_email_address'])
