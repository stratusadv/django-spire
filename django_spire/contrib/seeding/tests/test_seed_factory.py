import pytest
from django.test import TestCase

from django_spire.contrib.seeding import Seeder
from django_spire.contrib.seeding.exceptions import DjangoSpireSeederError
from django_spire.contrib.seeding.seed.factory.base import BaseSeedFactory
from django_spire.contrib.seeding.field.seed.base import BaseFieldSeed


class DummyFieldSeed(BaseFieldSeed):
    def __init__(self, value=None):
        self.value = value

    def generate_value(self, seed_index):
        return self.value


class DummySeeder(Seeder):
    model_class = None
    cache_enabled = False
    fields_seeds = {
        'name': Seeder.static('Test'),
    }


class TestBaseSeedFactory(TestCase):
    def test_instantiation_requires_seeder(self):
        from django_spire.contrib.seeding.seed.factory.factory import SeedFactory

        seeder = DummySeeder(count=1, verbose=False)
        factory = SeedFactory(seeder=seeder)
        assert factory.seeder is not None
        assert factory.current_progress == 0


class TestSeedFactory(TestCase):
    def test_generates_seeds_list(self):
        from django_spire.contrib.seeding.seed.factory.factory import SeedFactory

        seeder = DummySeeder(count=3, verbose=False)
        factory = SeedFactory(seeder=seeder)
        seeds = factory.generate_seeds(count=3, cache_enabled=False, cache_name='test_cache')

        assert isinstance(seeds, list)
        assert len(seeds) == 3

    def test_generate_seeds_returns_seed_objects(self):
        from django_spire.contrib.seeding.seed.factory.factory import SeedFactory

        seeder = DummySeeder(count=2, verbose=False)
        factory = SeedFactory(seeder=seeder)
        seeds = factory.generate_seeds(count=2, cache_enabled=False, cache_name='test_cache')

        for seed in seeds:
            assert hasattr(seed, 'to_dict')
            assert hasattr(seed, '__getitem__')

    def test_generate_seeds_with_different_counts(self):
        from django_spire.contrib.seeding.seed.factory.factory import SeedFactory

        seeder = DummySeeder(count=1, verbose=False)
        factory = SeedFactory(seeder=seeder)

        for count in [0, 1, 5, 10]:
            seeds = factory.generate_seeds(count=count, cache_enabled=False, cache_name='test_cache')
            assert len(seeds) == count

    def test_generate_seeds_creates_fields_from_seeds_config(self):
        from django_spire.contrib.seeding.seed.factory.factory import SeedFactory

        class ConfigSeeder(Seeder):
            model_class = None
            cache_enabled = False
            fields_seeds = {
                'field_a': Seeder.static('value_a'),
                'field_b': Seeder.static('value_b'),
            }

        seeder = ConfigSeeder(count=1, verbose=False)
        factory = SeedFactory(seeder=seeder)
        seeds = factory.generate_seeds(count=1, cache_enabled=False, cache_name='test_cache')

        assert seeds[0]['field_a'] == 'value_a'
        assert seeds[0]['field_b'] == 'value_b'