from uuid import uuid4

from django.db import migrations, models


def fill_keys(apps, schema_editor):
    subdomain_model = apps.get_model('django_spire_metric_domain', 'SubDomain')
    rows = list(subdomain_model.objects.filter(key__isnull=True))
    for row in rows:
        row.key = uuid4()
    subdomain_model.objects.bulk_update(rows, ['key'])


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ('django_spire_metric_domain', '0002_statisticvalue_sub_domain'),
    ]

    operations = [
        migrations.AddField(
            model_name='subdomain',
            name='key',
            field=models.UUIDField(default=uuid4, editable=False, null=True, unique=True),
        ),
        migrations.RunPython(fill_keys, noop),
        migrations.AlterField(
            model_name='subdomain',
            name='key',
            field=models.UUIDField(default=uuid4, editable=False, unique=True),
        ),
    ]
