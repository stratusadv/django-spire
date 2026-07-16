import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'test_project.postgres_settings')
os.environ.setdefault('DANDY_SETTINGS_MODULE', 'test_project.dandy_settings')

application = get_wsgi_application()

from django.contrib.auth.models import User

from django_spire.contrib.seeding import Seeder
from test_project.app.task.choices import TaskStatusChoices, TaskUserRoleChoices
from test_project.app.task.models import Task, TaskUser


class TaskModelSeeder(Seeder):
    model_class = Task
    cache_enabled = False

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


task_model_seeder = TaskModelSeeder(count=20)
task_model_seeder.seed_database()


class SubTaskModelSeeder(Seeder):
    model_class = Task
    cache_enabled = False

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


class TaskUserModelSeeder(Seeder):
    model_class = TaskUser
    cache_enabled = False

    fields_seeds = {
        'id': Seeder.exclude(),
        'user_id': Seeder.model.random_foreign_key(User),
        'task_id': Seeder.model.random_foreign_key(Task),
        'role': Seeder.model.random_field_choice(TaskUserRoleChoices),
        'created_datetime': Seeder.fake.date_time_between(start_date='-30d', end_date='now'),
        'is_active': Seeder.static(True),
        'is_deleted': Seeder.static(False),
    }


sub_task_model_seeder = SubTaskModelSeeder(count=100)
sub_task_model_seeder.seed_database()

task_user_model_seeder = TaskUserModelSeeder(count=400)
task_user_model_seeder.seed_database()
