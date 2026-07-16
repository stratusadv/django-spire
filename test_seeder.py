import os
import random
from time import sleep

from django.core.wsgi import get_wsgi_application

from test_project.app.task.choices import TaskStatusChoices

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'test_project.postgres_settings')
os.environ.setdefault('DANDY_SETTINGS_MODULE', 'test_project.dandy_settings')

application = get_wsgi_application()

from test_project.app.task.models import Task  # noqa

from django_spire.contrib.seeding import Seeder  # noqa


def random_boolean(true_weight: float = 0.5) -> bool:
    number = random.random()
    return number <= true_weight


class TaskSeeder(Seeder):
    model_class = Task

    # cache_enabled = True

    fields_seeds = {
        # 'id': Seeder.exclude(),
        'parent_id': Seeder.model.random_foreign_key(Task),
        'name': Seeder.fake.sentence(),
        'status': Seeder.model.random_field_choice(TaskStatusChoices),
        'description': Seeder.llm.automatic(str),
        'created_datetime': Seeder.fake.date_time_between(start_date='-30d', end_date='now'),
        'is_active': Seeder.static(True),
        'is_deleted': Seeder.custom.callable(random_boolean, true_weight=0.8),
    }

    # def __post_seed__(self) -> None:
    #     for seed in self.seeds:
    #         seed['parent_id'] = 10
    #
    # def __post_seed_database__(self) -> None:
    #     sleep(2)


task_seeder = TaskSeeder(count=100)

task_seeder.seed(1)

tasks = task_seeder.to_list_of_dicts()

print(f'{task_seeder.queryset.filter(is_deleted=False).count()=}')
print(f'{Task.objects.all().count()=}')
