import enum

from django.test import TestCase

from django_spire.contrib.seeding import Seeder
from django_spire.contrib.seeding.field.seed.callable_seed import CallableFieldSeed
from django_spire.contrib.seeding.field.seed.model_seed import OrderedForeignKeyModelFieldSeed
from django_spire.contrib.seeding.field.seed.random_seed import RandomFieldSeed


class TestModelFieldSeedHelper(TestCase):
    def test_random_field_choice_returns_random_field_seed(self):
        class Status(enum.Enum):
            PENDING = 'pending'
            ACTIVE = 'active'
            COMPLETED = 'completed'

        seed = Seeder.model.random_field_choice(Status)
        assert isinstance(seed, RandomFieldSeed)
        assert seed.enum_ is Status

    def test_random_field_choice_generates_enum_value(self):
        class Status(enum.Enum):
            A = 'a'
            B = 'b'

        seed = Seeder.model.random_field_choice(Status)
        value = seed.generate_value(0)
        assert value in list(Status)

    def test_random_field_choice_with_django_choices(self):
        from django.db.models import TextChoices

        class Status(TextChoices):
            PENDING = 'pending', 'Pending'
            ACTIVE = 'active', 'Active'
            COMPLETED = 'completed', 'Completed'

        seed = Seeder.model.random_field_choice(Status)
        assert isinstance(seed, RandomFieldSeed)
        value = seed.generate_value(0)
        assert value in list(Status)