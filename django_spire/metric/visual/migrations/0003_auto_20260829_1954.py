from django.db import migrations


def backfill_visual_references(apps, schema_editor):  # noqa: ARG001
    Visual = apps.get_model('django_spire_metric_visual', 'Visual')
    VisualReference = apps.get_model('django_spire_metric_visual', 'VisualReference')

    rows = [
        VisualReference(visual_id=visual.pk, reference=visual.reference, order=0)
        for visual in Visual.objects.exclude(reference='')
    ]

    VisualReference.objects.bulk_create(rows)


class Migration(migrations.Migration):

    dependencies = [
        ('django_spire_metric_visual', '0002_remove_visual_reference_visualreference'),
    ]

    operations = [
        migrations.RunPython(backfill_visual_references, migrations.RunPython.noop),
    ]
