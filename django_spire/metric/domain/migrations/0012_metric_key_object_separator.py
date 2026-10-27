from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from django.db import migrations

if TYPE_CHECKING:
    from django.db.migrations.schema import MigrationSchemaEditor
    from django.db.migrations.state import ProjectState

logger = logging.getLogger(__name__)

KEYED_MODELS = (
    ('django_spire_metric_domain', 'domain'),
    ('django_spire_metric_domain', 'subdomain'),
    ('django_spire_metric_domain', 'statisticgroup'),
    ('django_spire_metric_domain', 'statistic'),
)


def rewrite_keys(
    apps: ProjectState, _schema_editor: MigrationSchemaEditor, *, source: str, target: str
) -> None:
    for app_label, model_name in KEYED_MODELS:
        model = apps.get_model(app_label, model_name)
        for row in model.objects.filter(key__contains=source):
            new_key = row.key.replace(source, target)
            collision = model.objects.filter(key=new_key).exclude(pk=row.pk).exists()
            if collision:
                logger.warning(
                    'Metric key migration skipped %s %r: %r is already in use', model_name, row.key, new_key
                )
                continue
            row.key = new_key
            row.save(update_fields=['key'])


def forward(apps: ProjectState, schema_editor: MigrationSchemaEditor) -> None:
    rewrite_keys(apps, schema_editor, source='__', target='--')


def reverse(apps: ProjectState, schema_editor: MigrationSchemaEditor) -> None:
    rewrite_keys(apps, schema_editor, source='--', target='__')


class Migration(migrations.Migration):
    dependencies = [('django_spire_metric_domain', '0011_domain_is_orphaned_statistic_is_orphaned_and_more')]

    operations = [migrations.RunPython(forward, reverse)]
