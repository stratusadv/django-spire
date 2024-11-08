# Generated by Django 5.1.3 on 2024-11-08 22:57

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
            name='File',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_active', models.BooleanField(default=True, editable=False)),
                ('is_deleted', models.BooleanField(default=False, editable=False)),
                ('created_datetime', models.DateTimeField(default=django.utils.timezone.localtime, editable=False)),
                ('object_id', models.PositiveIntegerField(blank=True, editable=False, null=True)),
                ('file', models.FileField(max_length=500, upload_to='')),
                ('name', models.CharField(default='', editable=False, max_length=255)),
                ('type', models.CharField(default='', editable=False, max_length=255)),
                ('size', models.CharField(default='', editable=False, max_length=64)),
                ('related_field', models.CharField(blank=True, editable=False, max_length=3, null=True)),
                ('content_type', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype')),
            ],
            options={
                'verbose_name': 'File',
                'verbose_name_plural': 'Files',
                'db_table': 'spire_file',
                'indexes': [models.Index(fields=['content_type', 'object_id'], name='spire_file_content_04cd73_idx')],
            },
        ),
    ]
