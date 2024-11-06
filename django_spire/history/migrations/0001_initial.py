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
            name='ActivityLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('object_id', models.PositiveIntegerField(editable=False)),
                ('verb', models.CharField(max_length=64)),
                ('information', models.TextField(blank=True, null=True)),
                ('created_datetime', models.DateTimeField(default=django.utils.timezone.localtime)),
                ('content_type', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype')),
                ('recipient', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='actors', related_query_name='actor', to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='users', related_query_name='user', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Activities',
                'verbose_name_plural': 'Activities',
                'ordering': ['-created_datetime'],
            },
        ),
        migrations.CreateModel(
            name='ActivitySubscriber',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_datetime', models.DateTimeField(default=django.utils.timezone.localtime)),
                ('activity', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subscribers', related_query_name='subscriber', to='spire_history.activitylog')),
                ('subscriber', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='activity_subscribers', related_query_name='activity_subscriber', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='EventHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('object_id', models.PositiveIntegerField(editable=False)),
                ('event', models.CharField(choices=[('crea', 'Created'), ('upda', 'Updated'), ('acti', 'Active'), ('inac', 'Inactive'), ('dele', 'Deleted'), ('unde', 'Un-Deleted')], default='upda', max_length=4)),
                ('created_datetime', models.DateTimeField(default=django.utils.timezone.localtime)),
                ('content_type', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype')),
            ],
            options={
                'verbose_name': 'Event History',
                'verbose_name_plural': 'Event History',
            },
        ),
        migrations.CreateModel(
            name='View',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('object_id', models.PositiveIntegerField(editable=False)),
                ('created_datetime', models.DateTimeField(default=django.utils.timezone.localtime, editable=False)),
                ('content_type', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype')),
                ('user', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='views', related_query_name='view', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'View',
                'verbose_name_plural': 'Views',
            },
        ),
    ]
