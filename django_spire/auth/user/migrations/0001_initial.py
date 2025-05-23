# Generated by Django 5.2 on 2025-04-23 17:23

import django.contrib.auth.models
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='AuthUser',
            fields=[
            ],
            options={
                'verbose_name': 'Auth User',
                'verbose_name_plural': 'Auth Users',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('auth.user', models.Model),
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
    ]
