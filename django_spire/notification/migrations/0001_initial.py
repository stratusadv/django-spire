# Generated by Django 5.1.3 on 2024-11-06 20:22

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(default='email', max_length=32)),
                ('email', models.EmailField(default='', max_length=254)),
                ('name', models.CharField(blank=True, max_length=124, null=True)),
                ('title', models.CharField(default='', max_length=128)),
                ('body', models.TextField(default='')),
                ('url', models.CharField(default='', max_length=255)),
                ('send_datetime', models.DateTimeField(default=django.utils.timezone.now)),
                ('created_datetime', models.DateTimeField(default=django.utils.timezone.now)),
                ('sent_datetime', models.DateTimeField(blank=True, null=True)),
                ('is_sent', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name': 'Notification',
                'verbose_name_plural': 'Notifications',
                'db_table': 'spire_notification',
            },
        ),
    ]
