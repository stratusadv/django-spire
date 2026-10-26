from __future__ import annotations

from typing import TYPE_CHECKING

from django.db import migrations, models

from django_spire.metric.key_utils import unique_key_from_name

if TYPE_CHECKING:
    from django.db.migrations.schema import MigrationSchemaEditor
    from django.db.migrations.state import ProjectState


def fill_domain_keys(apps: ProjectState, schema_editor: MigrationSchemaEditor) -> None:  # noqa: ARG001
    domain_model = apps.get_model('django_spire_metric_domain', 'Domain')
    for row in domain_model.objects.filter(key__isnull=True):
        row.key = unique_key_from_name(row)
        row.save(update_fields=['key'])


def fill_statisticgroup_keys(apps: ProjectState, schema_editor: MigrationSchemaEditor) -> None:  # noqa: ARG001
    group_model = apps.get_model('django_spire_metric_domain', 'StatisticGroup')
    for row in group_model.objects.filter(key__isnull=True):
        row.key = unique_key_from_name(row)
        row.save(update_fields=['key'])


def noop(apps: ProjectState, schema_editor: MigrationSchemaEditor) -> None:
    pass


class Migration(migrations.Migration):
    dependencies = [('django_spire_metric_domain', '0009_alter_statistic_key_alter_subdomain_key')]

    operations = [
        migrations.AddField(
            model_name='domain',
            name='key',
            field=models.SlugField(blank=True, max_length=64, null=True, unique=True),
        ),
        migrations.AddField(
            model_name='statisticgroup',
            name='key',
            field=models.SlugField(blank=True, max_length=64, null=True, unique=True),
        ),
        migrations.RunPython(fill_domain_keys, noop),
        migrations.RunPython(fill_statisticgroup_keys, noop),
        migrations.AlterField(
            model_name='domain',
            name='key',
            field=models.SlugField(blank=True, max_length=64, unique=True),
        ),
        migrations.AlterField(
            model_name='statisticgroup',
            name='key',
            field=models.SlugField(blank=True, max_length=64, unique=True),
        ),
    ]
