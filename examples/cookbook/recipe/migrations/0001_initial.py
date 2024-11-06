# Generated by Django 5.1.2 on 2024-11-06 03:56

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Recipe',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_active', models.BooleanField(default=True, editable=False)),
                ('is_deleted', models.BooleanField(default=False, editable=False)),
                ('created_datetime', models.DateTimeField(default=django.utils.timezone.localtime, editable=False)),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField(default='')),
                ('course', models.CharField(choices=[('bre', 'Breakfast'), ('app', 'Appetizer'), ('mai', 'Main Course'), ('des', 'Dessert'), ('sou', 'Soup'), ('sid', 'Side Dish'), ('sal', 'Salad')], default='mai', max_length=3)),
                ('prep_time', models.IntegerField(default=15)),
                ('cook_time', models.IntegerField(default=30)),
                ('servings', models.IntegerField(default=1)),
            ],
            options={
                'verbose_name': 'Recipe',
                'verbose_name_plural': 'Recipes',
                'db_table': 'cookbook_recipe',
            },
        ),
        migrations.CreateModel(
            name='NutritionFact',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_active', models.BooleanField(default=True, editable=False)),
                ('is_deleted', models.BooleanField(default=False, editable=False)),
                ('created_datetime', models.DateTimeField(default=django.utils.timezone.localtime, editable=False)),
                ('type', models.CharField(choices=[('prot', 'Protein'), ('carb', 'Carbohydrate'), ('fat', 'Fat')], max_length=255)),
                ('quantity', models.FloatField(default=0)),
                ('recipe', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='nutrition_facts', related_query_name='nutrition_fact', to='cookbook_recipe.recipe')),
            ],
            options={
                'verbose_name': 'Nutrition Fact',
                'verbose_name_plural': 'Nutrition Facts',
                'db_table': 'recipe_nutrition_fact',
            },
        ),
        migrations.CreateModel(
            name='Ingredient',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_active', models.BooleanField(default=True, editable=False)),
                ('is_deleted', models.BooleanField(default=False, editable=False)),
                ('created_datetime', models.DateTimeField(default=django.utils.timezone.localtime, editable=False)),
                ('name', models.CharField(max_length=255)),
                ('quantity', models.CharField(default='', max_length=255)),
                ('directions', models.TextField(default='')),
                ('recipe', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ingredients', related_query_name='ingredient', to='cookbook_recipe.recipe')),
            ],
            options={
                'verbose_name': 'Ingredient',
                'verbose_name_plural': 'Ingredients',
                'db_table': 'cookbook_ingredient',
            },
        ),
    ]
