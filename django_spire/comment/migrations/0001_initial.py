# Generated by Django 5.1.3 on 2024-11-06 20:22

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
            name='Comment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_active', models.BooleanField(default=True, editable=False)),
                ('is_deleted', models.BooleanField(default=False, editable=False)),
                ('object_id', models.PositiveIntegerField(editable=False)),
                ('information', models.TextField(default='')),
                ('created_datetime', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('is_edited', models.BooleanField(default=False, editable=False)),
                ('content_type', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype')),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', related_query_name='child', to='spire_comment.comment')),
                ('user', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='comment_list', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Comment',
                'verbose_name_plural': 'Comments',
                'db_table': 'spire_comment',
                'ordering': ['-created_datetime'],
            },
        ),
    ]
