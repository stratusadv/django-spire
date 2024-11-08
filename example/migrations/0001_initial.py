# Generated by Django 5.1.2 on 2024-11-08 01:38

import django.core.validators
import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='TestModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_active', models.BooleanField(default=True, editable=False)),
                ('is_deleted', models.BooleanField(default=False, editable=False)),
                ('created_datetime', models.DateTimeField(default=django.utils.timezone.localtime, editable=False)),
                ('first_name', models.CharField(max_length=32)),
                ('last_name', models.CharField(max_length=32)),
                ('description', models.TextField()),
                ('personality_type', models.CharField(choices=[('int', 'Introvert'), ('ext', 'Extrovert')], default='int', max_length=3)),
                ('email', models.EmailField(blank=True, max_length=254, null=True)),
                ('favorite_number', models.IntegerField(validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(999)])),
                ('anniversary_datetime', models.DateTimeField(default=django.utils.timezone.now)),
                ('birth_date', models.DateField(default=django.utils.timezone.localdate)),
                ('weight_lbs', models.DecimalField(decimal_places=3, max_digits=7)),
                ('bed_time', models.TimeField(default='20:00')),
                ('likes_to_party', models.BooleanField(default=True)),
                ('best_friend', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='example.testmodel')),
            ],
            options={
                'verbose_name': 'Test Model',
                'verbose_name_plural': 'Test Model',
                'db_table': 'spire_test_model',
            },
        ),
    ]
