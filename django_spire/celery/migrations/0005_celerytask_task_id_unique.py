# Generated for CeleryTaskRunner (phase 1)

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('django_spire_celery', '0004_alter_celerytask_state'),
    ]

    operations = [
        migrations.AlterField(
            model_name='celerytask',
            name='task_id',
            field=models.UUIDField(editable=False, unique=True, verbose_name='Celery Task ID'),
        ),
    ]
