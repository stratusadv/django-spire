import random

from django.contrib.auth.models import User
from django.db.models import Model

from django_spire.contrib.seeding import DjangoModelSeeder
from test_project.app.task.models import Task, TaskUser


class TaskModelSeeder(DjangoModelSeeder):
    model_class = Task
    cache_name = 'queryset_task_seeder'

    fields = {
        'id': 'exclude',
        'parent_id': 'exclude',
        'name': ('faker', 'sentence', {'nb_words': 5}),
        'description': ('faker',),
        'created_datetime': (
            'custom',
            'date_time_between',
            {'start_date': '-30d', 'end_date': 'now'},
        ),
        'is_active': True,
        'is_deleted': False,
    }

    default_to = 'faker'


class SubTaskModelSeeder(DjangoModelSeeder):
    model_class = Task
    cache_name = 'queryset_sub_task_seeder'

    fields = {
        'id': 'exclude',
        'parent_id': (
            'faker',
            'random_element',
            {'elements': Task.objects.filter(parent_id=None).values_list('id', flat=True)},
        ),
        'name': ('faker', 'sentence', {'nb_words': 5}),
        'description': ('faker',),
        'created_datetime': (
            'custom',
            'date_time_between',
            {'start_date': '-30d', 'end_date': 'now'},
        ),
        'is_active': True,
        'is_deleted': False,
    }

    default_to = 'faker'


class TaskUserModelSeeder(DjangoModelSeeder):
    model_class = TaskUser
    cache_name = 'task_task_user_seeder'

    fields = {
        'id': 'exclude',
        'user_id': (
            'faker',
            'random_element',
            {'elements': User.objects.all().values_list('id', flat=True)},
        ),
        'task_id': (
            'faker',
            'random_element',
            {'elements': Task.objects.filter(parent_id=None).values_list('id', flat=True)},
        ),
        'role': 'faker',
        'created_datetime': (
            'custom',
            'date_time_between',
            {'start_date': '-30d', 'end_date': 'now'},
        ),
        'is_active': True,
        'is_deleted': False,
    }

    default_to = 'faker'
