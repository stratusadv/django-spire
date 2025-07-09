from django.contrib.auth.models import User
from django.db.models import Model

from django_spire.contrib.seeding import DjangoModelSeeder
from test_project.apps.queryset_filtering.models import Task, TaskUser


class TaskModelSeeder(DjangoModelSeeder):
    model_class = Task
    cache_name = 'queryset_task_seeder'

    fields = {
        'id': 'exclude',
        'name': ('llm', 'Things that you do at home when no one is looking.'),
        'description': ('llm', 'Describe the things you do.'),
        'created_datetime': ('custom', 'date_time_between', {'start_date': '-30d', 'end_date': 'now'}),
        'is_active': True,
        'is_deleted': False,
    }

    default_to = 'faker'


class TaskUserModelSeeder(DjangoModelSeeder):
    model_class = TaskUser
    cache_name = 'queryset_filtering_task_user_seeder'

    fields = {
        'id': 'exclude',
        'user_id': 'exclude',
        'task_id': 'exclude',
        'role': 'faker',
        'created_datetime': ('custom', 'date_time_between', {'start_date': '-30d', 'end_date': 'now'}),
        'is_active': True,
        'is_deleted': False,
    }

    default_to = 'faker'

    @classmethod
    def seed_database(
            cls,
            count = 1,
            fields: dict | None = None
    ) -> list[Model]:
        if fields is None:
            fields = {}

        return super().seed_database(
            count=count,
            fields= fields | {
                'user_id': ('custom', 'fk_in_order', {'model_class': User}),
                'task_id': ('custom', 'fk_random', {'model_class': Task}),
            }
        )
