# Generated by Django 5.1.6 on 2025-03-07 22:00

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
                ('activity', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subscribers', related_query_name='subscriber', to='spire_history_activity.activitylog')),
                ('subscriber', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='activity_subscribers', related_query_name='activity_subscriber', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
