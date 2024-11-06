# Generated by Django 5.1.3 on 2024-11-06 20:22

import django.contrib.auth.models
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='PortalGroup',
            fields=[
            ],
            options={
                'verbose_name': 'Group',
                'verbose_name_plural': 'Groups',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('auth.group', models.Model),
            managers=[
                ('objects', django.contrib.auth.models.GroupManager()),
            ],
        ),
        migrations.CreateModel(
            name='PortalUser',
            fields=[
            ],
            options={
                'verbose_name': 'User',
                'verbose_name_plural': 'Users',
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
