# Generated by Django 5.1.2 on 2024-10-31 16:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('playground', '0002_testmodel_created_datetime_testmodel_is_active_and_more'),
    ]

    operations = [
        migrations.DeleteModel(
            name='TestModel',
        ),
    ]
