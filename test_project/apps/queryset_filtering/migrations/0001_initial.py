# Generated by Django 5.2.1 on 2025-07-09 14:40

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_active', models.BooleanField(default=True, editable=False)),
                ('is_deleted', models.BooleanField(default=False, editable=False)),
                ('created_datetime', models.DateTimeField(default=django.utils.timezone.localtime, editable=False)),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField(default='')),
                ('status', models.CharField(choices=[('new', 'New'), ('inp', 'In Progress'), ('com', 'Complete'), ('can', 'Cancelled')], default='new', max_length=3)),
            ],
            options={
                'verbose_name': 'Task',
                'verbose_name_plural': 'Tasks',
                'db_table': 'test_project_queryset_filtering_task',
            },
        ),
        migrations.CreateModel(
            name='TaskUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_active', models.BooleanField(default=True, editable=False)),
                ('is_deleted', models.BooleanField(default=False, editable=False)),
                ('created_datetime', models.DateTimeField(default=django.utils.timezone.localtime, editable=False)),
                ('role', models.CharField(choices=[('lea', 'Leader'), ('sup', 'Support'), ('fol', 'Follower')], default='lea', max_length=3)),
                ('task', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='users', related_query_name='user', to='test_project_queryset_filtering.task')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tasks', related_query_name='task', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Task User',
                'verbose_name_plural': 'Tasks Users',
                'db_table': 'test_project_queryset_filtering_task_user',
            },
        ),
    ]
