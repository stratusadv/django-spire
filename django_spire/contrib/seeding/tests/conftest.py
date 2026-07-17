import enum

import pytest

from django_spire.contrib.seeding import Seeder
from django_spire.contrib.seeding.field.seed.static_seed import StaticFieldSeed


class TestStatusChoices(enum.Enum):
    PENDING = 'pending'
    ACTIVE = 'active'
    COMPLETED = 'completed'


class TestSeeder(Seeder):
    model_class = None
    cache_enabled = False
    locale = 'en_CA'
    fields_seeds = {
        'name': Seeder.fake.name(),
        'status': Seeder.static(TestStatusChoices.ACTIVE),
        'count': Seeder.random.int(a=1, b=10),
        'description': Seeder.llm(str, 'A test description'),
        'created': Seeder.fake.date_time_between(),
    }


@pytest.fixture
def test_seeder():
    return TestSeeder(count=5, verbose=False)


@pytest.fixture
def simple_seeder():
    class SimpleSeeder(Seeder):
        model_class = None
        cache_enabled = False
        fields_seeds = {
            'name': StaticFieldSeed('Test Name'),
            'value': StaticFieldSeed(42),
        }

    return SimpleSeeder(count=3, verbose=False)


@pytest.fixture
def seeder_with_llm():
    return TestSeeder(count=2, verbose=False)