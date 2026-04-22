import logging

from django.db import migrations, models


logger = logging.getLogger(__name__)


SIZE_MULTIPLIERS = {
    'KB': 1_024,
    'MB': 1_048_576,
    'GB': 1_073_741_824,
    'TB': 1_099_511_627_776,
}

REVERSE_THRESHOLDS = [
    (1_099_511_627_776, 'TB'),
    (1_073_741_824, 'GB'),
    (1_048_576, 'MB'),
    (1_024, 'KB'),
]


def nulls_to_empty(apps, schema_editor):
    File = apps.get_model('django_spire_file', 'File')
    File.objects.filter(related_field__isnull=True).update(related_field='')


def convert_size_strings(apps, schema_editor):
    File = apps.get_model('django_spire_file', 'File')
    batch = []
    failed = []

    for file_obj in File.objects.iterator(chunk_size=1000):
        size_bytes = 0

        if file_obj.size:
            raw = file_obj.size.strip()
            parts = raw.split(' ')

            if len(parts) != 2:
                failed.append((file_obj.pk, raw))
            else:
                unit = parts[1].upper()
                multiplier = SIZE_MULTIPLIERS.get(unit)

                if multiplier is None:
                    failed.append((file_obj.pk, raw))
                else:
                    try:
                        size_bytes = int(float(parts[0]) * multiplier)
                    except ValueError:
                        failed.append((file_obj.pk, raw))

        file_obj.size_bytes = size_bytes
        batch.append(file_obj)

        if len(batch) >= 1000:
            File.objects.bulk_update(batch, ['size_bytes'])
            batch = []

    if batch:
        File.objects.bulk_update(batch, ['size_bytes'])

    if failed:
        for pk, raw in failed:
            logger.warning('File id=%s: could not parse size %r, defaulted to 0', pk, raw)

        raise RuntimeError(
            f'Failed to parse size for {len(failed)} file(s): '
            f'{", ".join(str(pk) for pk, _ in failed)}. '
            f'Check warnings above. If these rows are acceptable as 0 bytes, '
            f'remove this raise and re-run.'
        )


def revert_size_to_strings(apps, schema_editor):
    File = apps.get_model('django_spire_file', 'File')
    batch = []

    for file_obj in File.objects.iterator(chunk_size=1000):
        size_str = '0 kb'

        if file_obj.size_bytes > 0:
            for threshold, unit in REVERSE_THRESHOLDS:
                if file_obj.size_bytes >= threshold:
                    size_str = f'{round(file_obj.size_bytes / threshold, 2)} {unit.lower()}'
                    break
            else:
                size_str = f'{round(file_obj.size_bytes / 1_024, 2)} kb'

        file_obj.size = size_str
        batch.append(file_obj)

        if len(batch) >= 1000:
            File.objects.bulk_update(batch, ['size'])
            batch = []

    if batch:
        File.objects.bulk_update(batch, ['size'])


class Migration(migrations.Migration):
    atomic = True

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
        migrations.RunPython(convert_size_strings, revert_size_to_strings),
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
