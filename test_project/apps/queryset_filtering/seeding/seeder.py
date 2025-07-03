import django
django.setup()

from django_spire.contrib.seeding import DjangoModelSeeder
from test_project.apps.queryset_filtering.models import Task


class TaskModelSeeder(DjangoModelSeeder):
    model_class = Task
    cache_name = 'queryset_filtering_task_seeder'

    fields = {
        'id': 'exclude',
        'name': ('llm', 'Things that you do at home when no one is looking.'),
        'description': ('llm', 'Describe the things you do.'),
        'created_datetime': ('custom', 'date_time_between', {'start_date': '-30d', 'end_date': 'now'}),
        'is_active': True,
        'is_deleted': False,
    }

    default_to = 'faker'


if __name__ == '__main__':
    TaskModelSeeder.seed_database(20)
    print('seeded!')