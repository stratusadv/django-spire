from __future__ import annotations

from django.db import migrations, models
from django.db.models.deletion import CASCADE
from django.utils import timezone


def normalize_values(apps, schema_editor):
    from datetime import datetime, time

    value_model = apps.get_model('django_spire_metric_domain', 'StatisticValue')
    subdomain_model = apps.get_model('django_spire_metric_domain', 'SubDomain')

    local_tz = timezone.get_current_timezone()
    rows = list(value_model.objects.all())

    for row in rows:
        local_day = row.timestamp.astimezone(local_tz).date()
        row.timestamp = timezone.make_aware(datetime.combine(local_day, time.min), local_tz)

        if row.sub_domain_id is None:
            statistic = row.statistic
            candidate = subdomain_model.objects.filter(domain=statistic.group.domain).first()
            if candidate is None:
                candidate = subdomain_model.objects.first()
            if candidate is not None:
                row.sub_domain_id = candidate.pk

    value_model.objects.bulk_update(rows, ['timestamp', 'sub_domain_id'])


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [('django_spire_metric_domain', '0001_initial')]

    operations = [
        migrations.RemoveConstraint(
            model_name='statisticvalue', name='unique_statistic_value_reference_date'
        ),
        migrations.RemoveField(model_name='statisticvalue', name='updated_datetime'),
        migrations.RenameField(model_name='statisticvalue', old_name='date', new_name='timestamp'),
        migrations.AlterField(
            model_name='statisticvalue',
            name='timestamp',
            field=models.DateTimeField(default=timezone.now),
        ),
        migrations.AddField(
            model_name='statisticvalue',
            name='sub_domain',
            field=models.ForeignKey(
                null=True,
                on_delete=CASCADE,
                related_name='values',
                related_query_name='value',
                to='django_spire_metric_domain.subdomain',
            ),
        ),
        migrations.AddIndex(
            model_name='statisticvalue',
            index=models.Index(fields=['statistic', 'timestamp'], name='ix_statistic_timestamp'),
        ),
        migrations.AddIndex(
            model_name='statisticvalue',
            index=models.Index(
                fields=['statistic', 'sub_domain', 'timestamp'], name='ix_statistic_subdomain_ts'
            ),
        ),
        migrations.RunPython(normalize_values, noop),
        migrations.AlterField(
            model_name='statisticvalue',
            name='sub_domain',
            field=models.ForeignKey(
                on_delete=CASCADE,
                related_name='values',
                related_query_name='value',
                to='django_spire_metric_domain.subdomain',
            ),
        ),
    ]
