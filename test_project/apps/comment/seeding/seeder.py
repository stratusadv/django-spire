from django_spire.contrib.seeding import DjangoModelSeeder
from test_project.apps.comment.models import CommentExample


class CommentExampleSeeder(DjangoModelSeeder):
    model_class = CommentExample
    cache_name = 'queryset_task_seeder'

    fields = {
        'id': 'exclude',
        'name': ('faker'),
        'description': ('faker'),
        'created_datetime': ('custom', 'date_time_between', {'start_date': '-30d', 'end_date': 'now'}),
        'is_active': True,
        'is_deleted': False,
    }

    default_to = 'faker'