# Generated by Django 5.1.7 on 2025-03-27 22:22

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='EventHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('object_id', models.PositiveIntegerField(editable=False)),
                ('event', models.CharField(choices=[('crea', 'Created'), ('upda', 'Updated'), ('acti', 'Active'), ('inac', 'Inactive'), ('dele', 'Deleted'), ('unde', 'Un-Deleted')], default='upda', max_length=4)),
                ('created_datetime', models.DateTimeField(default=django.utils.timezone.localtime)),
                ('content_type', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='spire_eventhistory', to='contenttypes.contenttype')),
            ],
            options={
                'verbose_name': 'Event History',
                'verbose_name_plural': 'Event History',
                'db_table': 'spire_history_event_history',
            },
        ),
    ]
