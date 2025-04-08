# Generated by Django 5.2 on 2025-04-07 21:43

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_active', models.BooleanField(default=True, editable=False)),
                ('is_deleted', models.BooleanField(default=False, editable=False)),
                ('created_datetime', models.DateTimeField(default=django.utils.timezone.localtime, editable=False)),
                ('type', models.CharField(choices=[('app', 'App'), ('email', 'Email'), ('push', 'Push'), ('sms', 'Sms')], default='email', max_length=32)),
                ('title', models.CharField(max_length=124)),
                ('body', models.TextField(default='')),
                ('processed_datetime', models.DateTimeField(blank=True, null=True)),
                ('url', models.CharField(default='', max_length=255)),
                ('is_processed', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name': 'Notification',
                'verbose_name_plural': 'Notifications',
                'db_table': 'spire_notification',
            },
        ),
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
        migrations.CreateModel(
            name='AppNotification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_active', models.BooleanField(default=True, editable=False)),
                ('is_deleted', models.BooleanField(default=False, editable=False)),
                ('created_datetime', models.DateTimeField(default=django.utils.timezone.localtime, editable=False)),
                ('url', models.CharField(default='', max_length=255)),
                ('object_id', models.PositiveIntegerField()),
                ('content_type', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='spire_appnotification', to='contenttypes.contenttype')),
                ('user', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('notification', models.OneToOneField(editable=False, on_delete=django.db.models.deletion.CASCADE, to='spire_notification.notification')),
            ],
            options={
                'verbose_name': 'App Notification',
                'verbose_name_plural': 'App Notifications',
                'db_table': 'spire_notification_app',
            },
        ),
    ]
