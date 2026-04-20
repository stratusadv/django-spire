from django.db import migrations, models


SIZE_MULTIPLIERS = {
    'KB': 1_000,
    'MB': 1_000_000,
    'GB': 1_000_000_000,
    'TB': 1_000_000_000_000,
}


def nulls_to_empty(apps, schema_editor):
    File = apps.get_model('django_spire_file', 'File')
    File.objects.filter(related_field__isnull=True).update(related_field='')


def convert_size_strings(apps, schema_editor):
    File = apps.get_model('django_spire_file', 'File')
    batch = []

    for file_obj in File.objects.iterator(chunk_size=1000):
        size_bytes = 0

        if file_obj.size:
            parts = file_obj.size.strip().split(' ')

            if len(parts) == 2:
                try:
                    size_bytes = int(float(parts[0]) * SIZE_MULTIPLIERS.get(parts[1].upper(), 1))
                except (ValueError, KeyError):
                    pass

        file_obj.size_bytes = size_bytes
        batch.append(file_obj)

        if len(batch) >= 1000:
            File.objects.bulk_update(batch, ['size_bytes'])
            batch = []

    if batch:
        File.objects.bulk_update(batch, ['size_bytes'])


class Migration(migrations.Migration):

    dependencies = [
        ('django_spire_file', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(nulls_to_empty, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='file',
            name='related_field',
            field=models.CharField(blank=True, default='', editable=False, max_length=50),
        ),
        migrations.AddField(
            model_name='file',
            name='size_bytes',
            field=models.PositiveBigIntegerField(default=0, editable=False),
        ),
        migrations.RunPython(convert_size_strings, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name='file',
            name='size',
        ),
        migrations.RenameField(
            model_name='file',
            old_name='size_bytes',
            new_name='size',
        ),
    ]
