# Generated by Django 5.1.3 on 2024-11-08 22:57

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='SearchExample',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_active', models.BooleanField(default=True, editable=False)),
                ('is_deleted', models.BooleanField(default=False, editable=False)),
                ('created_datetime', models.DateTimeField(default=django.utils.timezone.localtime, editable=False)),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField(default='')),
            ],
            options={
                'verbose_name': 'Search',
                'verbose_name_plural': 'Searches',
                'db_table': 'example_search',
            },
        ),
    ]
