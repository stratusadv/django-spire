# Generated by Django 5.1.7 on 2025-03-27 22:28

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('spire_notification', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='EmailNotification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subject', models.CharField(max_length=128)),
                ('email', models.EmailField(max_length=254)),
                ('notification', models.OneToOneField(editable=False, on_delete=django.db.models.deletion.CASCADE, to='spire_notification.notification')),
            ],
            options={
                'verbose_name': 'Email Notification',
                'verbose_name_plural': 'Email Notifications',
                'db_table': 'spire_notification_email',
            },
        ),
    ]
