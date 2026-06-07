from django_spire.contrib.seeding import DjangoModelSeeder

from test_project.app.celery.models import CeleryStalk


class CeleryStalkSeeder(DjangoModelSeeder):
    cache_name = 'celery_stalk_seeder'
    model_class = CeleryStalk
    fields = {
        'id': 'exclude',
        'is_crisp': ('faker', 'boolean'),
        'length': ('faker', 'pyfloat'),
    }
