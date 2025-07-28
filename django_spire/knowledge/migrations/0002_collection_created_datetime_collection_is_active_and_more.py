import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('django_spire_knowledge', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='collection',
            name='created_datetime',
            field=models.DateTimeField(default=django.utils.timezone.localtime, editable=False),
        ),
        migrations.AddField(
            model_name='collection',
            name='is_active',
            field=models.BooleanField(default=True, editable=False),
        ),
        migrations.AddField(
            model_name='collection',
            name='is_deleted',
            field=models.BooleanField(default=False, editable=False),
        ),
        migrations.AddField(
            model_name='entry',
            name='created_datetime',
            field=models.DateTimeField(default=django.utils.timezone.localtime, editable=False),
        ),
        migrations.AddField(
            model_name='entry',
            name='is_active',
            field=models.BooleanField(default=True, editable=False),
        ),
        migrations.AddField(
            model_name='entry',
            name='is_deleted',
            field=models.BooleanField(default=False, editable=False),
        ),
        migrations.AddField(
            model_name='entryversion',
            name='created_datetime',
            field=models.DateTimeField(default=django.utils.timezone.localtime, editable=False),
        ),
        migrations.AddField(
            model_name='entryversion',
            name='is_active',
            field=models.BooleanField(default=True, editable=False),
        ),
        migrations.AddField(
            model_name='entryversion',
            name='is_deleted',
            field=models.BooleanField(default=False, editable=False),
        ),
        migrations.AddField(
            model_name='entryversionblock',
            name='created_datetime',
            field=models.DateTimeField(default=django.utils.timezone.localtime, editable=False),
        ),
        migrations.AddField(
            model_name='entryversionblock',
            name='is_active',
            field=models.BooleanField(default=True, editable=False),
        ),
        migrations.AddField(
            model_name='entryversionblock',
            name='is_deleted',
            field=models.BooleanField(default=False, editable=False),
        ),
    ]
