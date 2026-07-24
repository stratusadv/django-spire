from django.contrib.auth.models import User

from django_spire.contrib.seeding import Seeder
from test_project.app.task.choices import TaskStatusChoices, TaskUserRoleChoices
from test_project.app.task.models import Task, TaskUser


class TaskModelSeeder(Seeder):
    model_class = Task

    fields_seeds = {
        'id': Seeder.exclude(),
        'parent_id': Seeder.exclude(),
        'name': Seeder.fake.sentence(),
        'description': Seeder.llm(str),
        'status': Seeder.model.random_field_choice(TaskStatusChoices),
        'created_datetime': Seeder.fake.date_time_between(start_date='-30d', end_date='now'),
        'is_active': Seeder.static(True),
        'is_deleted': Seeder.static(False),
    }


class SubTaskModelSeeder(Seeder):
    model_class = Task

    fields_seeds = {
        'id': Seeder.exclude(),
        'parent_id': Seeder.model.random_foreign_key(Task),
        'name': Seeder.fake.sentence(),
        'description': Seeder.llm(str),
        'status': Seeder.model.random_field_choice(TaskStatusChoices),
        'created_datetime': Seeder.fake.date_time_between(start_date='-30d', end_date='now'),
        'is_active': Seeder.static(True),
        'is_deleted': Seeder.static(False),
    }


class SubSubTaskModelSeeder(Seeder):
    model_class = Task

    fields_seeds = {
        'id': Seeder.exclude(),
        'parent_id': Seeder.model.random_queryset_foreign_key(
            Task.objects.filter(parent__isnull=False)
        ),
        'name': Seeder.fake.sentence(),
        'description': Seeder.llm(str),
        'status': Seeder.model.random_field_choice(TaskStatusChoices),
        'created_datetime': Seeder.fake.date_time_between(start_date='-30d', end_date='now'),
        'is_active': Seeder.static(True),
        'is_deleted': Seeder.static(False),
    }


class TaskUserModelSeeder(Seeder):
    model_class = TaskUser

    fields_seeds = {
        'id': Seeder.exclude(),
        'user_id': Seeder.model.random_foreign_key(User),
        'task_id': Seeder.model.random_foreign_key(Task),
        'role': Seeder.model.random_field_choice(TaskUserRoleChoices),
        'created_datetime': Seeder.fake.date_time_between(start_date='-30d', end_date='now'),
        'is_active': Seeder.static(True),
        'is_deleted': Seeder.static(False),
    }
