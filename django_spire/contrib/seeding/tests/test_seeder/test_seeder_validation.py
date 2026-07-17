import pytest
from django.test import TestCase

from django_spire.contrib.seeding import Seeder
from django_spire.contrib.seeding.exceptions import DjangoSpireSeederError
from django_spire.contrib.seeding.field.seed.static_seed import StaticFieldSeed


class TestSeederValidation(TestCase):
    def test_empty_fields_seeds_is_valid(self):
        class EmptySeeder(Seeder):
            model_class = None
            cache_enabled = False
            fields_seeds = {}

        seeder = EmptySeeder(count=1, verbose=False)
        assert seeder.fields_seeds == {}

    def test_single_field_is_valid(self):
        class SingleFieldSeeder(Seeder):
            model_class = None
            cache_enabled = False
            fields_seeds = {'name': StaticFieldSeed('Test')}

        seeder = SingleFieldSeeder(count=1, verbose=False)
        assert 'name' in seeder.fields_seeds

    def test_valid_seeder_instantiation(self):
        class ValidSeeder(Seeder):
            model_class = None
            cache_enabled = False
            fields_seeds = {
                'name': StaticFieldSeed('Test'),
                'value': StaticFieldSeed(42),
            }

        seeder = ValidSeeder(count=1, verbose=False)
        assert seeder is not None
        assert len(seeder.fields_seeds) == 2


class TestSeederSubclassFieldsSeedsNone(TestCase):
    def test_valid_subclass_inherits_fields_seeds(self):
        class BaseSeeder(Seeder):
            model_class = None
            cache_enabled = False
            fields_seeds = {'name': StaticFieldSeed('Base')}

        class ChildSeeder(BaseSeeder):
            pass

        seeder = ChildSeeder(count=1, verbose=False)
        assert 'name' in seeder.fields_seeds
        assert seeder.fields_seeds['name'].value == 'Base'