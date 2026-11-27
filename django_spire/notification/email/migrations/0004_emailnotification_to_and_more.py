from __future__ import annotations

import ast
import json
import logging
import re

from django.db import migrations, models

import django_spire.notification.email.validators


logger = logging.getLogger(__name__)

CHUNK_SIZE = 1000
MAX_EMAIL_FIELD_LENGTH = 254


def _parse_recipient_string(raw: str) -> list[str]:
    stripped = raw.strip()

    if not stripped:
        return []

    if stripped.startswith('[') and stripped.endswith(']'):
        parsed = _parse_list_literal(stripped)

        if isinstance(parsed, list):
            return [
                item.strip()
                for item in parsed
                if isinstance(item, str) and item.strip()
            ]

    return [
        part.strip()
        for part in re.split(r'[,;]', stripped)
        if part.strip()
    ]


def _parse_list_literal(raw: str) -> object:
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        try:
            return ast.literal_eval(raw)
        except (SyntaxError, ValueError):
            return None


def _normalize_legacy_json_recipients(value: object) -> list[str]:
    if isinstance(value, str):
        return _parse_recipient_string(value)

    if isinstance(value, list):
        recipients: list[str] = []

        for item in value:
            if isinstance(item, str) and item.strip():
                recipients.extend(_parse_recipient_string(item))

        return recipients

    return []


def _dedupe_recipients(emails: list[str], seen: set[str]) -> list[str]:
    unique: list[str] = []

    for email in emails:
        key = email.lower()

        if key not in seen:
            seen.add(key)
            unique.append(email)

    return unique


def migrate_email_recipients(apps, schema_editor) -> None:
    EmailNotification = apps.get_model('django_spire_notification_email', 'EmailNotification')
    batch = []

    for email_notification in EmailNotification.objects.iterator(chunk_size=CHUNK_SIZE):
        raw_to = email_notification.to_email_address or ''
        parsed_to = _parse_recipient_string(raw_to)

        if not parsed_to:
            logger.warning(
                'EmailNotification id=%s has blank to_email_address; migrated to empty list',
                email_notification.pk,
            )

        seen: set[str] = set()
        email_notification.to = _dedupe_recipients(parsed_to, seen)
        email_notification.to_email_address = (
            email_notification.to[0][:MAX_EMAIL_FIELD_LENGTH] if email_notification.to else ''
        )
        email_notification.cc = _dedupe_recipients(
            _normalize_legacy_json_recipients(email_notification.cc),
            seen,
        )
        email_notification.bcc = _dedupe_recipients(
            _normalize_legacy_json_recipients(email_notification.bcc),
            seen,
        )
        batch.append(email_notification)

        if len(batch) >= CHUNK_SIZE:
            EmailNotification.objects.bulk_update(batch, ['to', 'to_email_address', 'cc', 'bcc'])
            batch = []

    if batch:
        EmailNotification.objects.bulk_update(batch, ['to', 'to_email_address', 'cc', 'bcc'])


def revert_email_recipients(apps, schema_editor) -> None:
    EmailNotification = apps.get_model('django_spire_notification_email', 'EmailNotification')
    batch = []

    for email_notification in EmailNotification.objects.iterator(chunk_size=CHUNK_SIZE):
        recipients = email_notification.to

        if isinstance(recipients, list) and recipients:
            if len(recipients) > 1:
                logger.warning(
                    'EmailNotification id=%s has %d recipients in to; keeping only the first on reverse migration',
                    email_notification.pk,
                    len(recipients),
                )

            email_notification.to_email_address = str(recipients[0])[:MAX_EMAIL_FIELD_LENGTH]
        else:
            email_notification.to_email_address = ''

        batch.append(email_notification)

        if len(batch) >= CHUNK_SIZE:
            EmailNotification.objects.bulk_update(batch, ['to_email_address'])
            batch = []

    if batch:
        EmailNotification.objects.bulk_update(batch, ['to_email_address'])


class Migration(migrations.Migration):
    atomic = True

    dependencies = [
        ('django_spire_notification_email', '0003_emailnotification_attachments'),
    ]

    operations = [
        migrations.AddField(
            model_name='emailnotification',
            name='to',
            field=models.JSONField(
                default=list,
                validators=[
                    django_spire.notification.email.validators.EmailListValidator(allow_empty=False)
                ],
            ),
        ),
        migrations.AlterField(
            model_name='emailnotification',
            name='bcc',
            field=models.JSONField(
                blank=True,
                default=list,
                validators=[
                    django_spire.notification.email.validators.EmailListValidator(allow_empty=True)
                ],
            ),
        ),
        migrations.AlterField(
            model_name='emailnotification',
            name='cc',
            field=models.JSONField(
                blank=True,
                default=list,
                validators=[
                    django_spire.notification.email.validators.EmailListValidator(allow_empty=True)
                ],
            ),
        ),
        migrations.AlterField(
            model_name='emailnotification',
            name='context_data',
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AlterField(
            model_name='emailnotification',
            name='template_id',
            field=models.CharField(blank=True, default='', max_length=64),
        ),
        migrations.AlterField(
            model_name='emailnotification',
            name='to_email_address',
            field=models.EmailField(
                blank=True,
                default='',
                help_text='Deprecated: use `to` instead.',
                max_length=254,
            ),
        ),
        migrations.RunPython(migrate_email_recipients, revert_email_recipients),
    ]
