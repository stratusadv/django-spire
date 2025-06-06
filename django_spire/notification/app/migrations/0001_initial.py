# Generated by Django 5.2.1 on 2025-05-15 20:20

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('django_spire_notification', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AppNotification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_active', models.BooleanField(default=True, editable=False)),
                ('is_deleted', models.BooleanField(default=False, editable=False)),
                ('created_datetime', models.DateTimeField(default=django.utils.timezone.localtime, editable=False)),
                ('template', models.TextField(default='django_spire/notification/app/item/notification_item.html')),
                ('context_data', models.JSONField(default=dict)),
                ('notification', models.OneToOneField(editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='app', related_query_name='app', to='django_spire_notification.notification')),
            ],
            options={
                'verbose_name': 'App Notification',
                'verbose_name_plural': 'App Notifications',
                'db_table': 'django_spire_notification_app',
            },
        ),
    ]
