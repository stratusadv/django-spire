from django_spire.contrib.seeding import Seeder
from test_project.app.comment.models import CommentExample


class CommentExampleSeeder(Seeder):
    model_class = CommentExample
    chech_enabled = True

    fields_seeds = {
        'id': Seeder.exclude(),
        'name': Seeder.fake.sentence(),
        'description': Seeder.llm(str),
        'created_datetime': Seeder.fake.date_time_between(start_date='-30d', end_date='now'),
        'is_active': Seeder.static(True),
        'is_deleted': Seeder.static(False),
    }
