from django.test import TestCase

from django_spire.contrib.seeding import Seeder
from django_spire.contrib.seeding.field.seed.static_seed import StaticFieldSeed
from django_spire.contrib.seeding.seed.factory.factory import SeedFactory


class TestBaseSeedFactoryInstantiation(TestCase):
    def test_instantiation_with_seeder(self):
        class DummySeeder(Seeder):
            model_class = None
            cache_enabled = False
            fields_seeds = {'field': StaticFieldSeed('value')}

        seeder = DummySeeder(count=1, verbose=False)
        factory = SeedFactory(seeder=seeder)
        assert factory.seeder is seeder

    def test_initializes_progress_to_zero(self):
        class DummySeeder(Seeder):
            model_class = None
            cache_enabled = False
            fields_seeds = {'field': StaticFieldSeed('value')}

        seeder = DummySeeder(count=1, verbose=False)
        factory = SeedFactory(seeder=seeder)
        assert factory.current_progress == 0


class TestBaseSeedFactoryProgress(TestCase):
    def test_progress_initializes_to_zero(self):
        class DummySeeder(Seeder):
            model_class = None
            cache_enabled = False
            fields_seeds = {'field': StaticFieldSeed('value')}

        seeder = DummySeeder(count=1, verbose=False)
        factory = SeedFactory(seeder=seeder)

        assert factory.current_progress == 0

    def test_seeder_verbose_attribute(self):
        class DummySeeder(Seeder):
            model_class = None
            cache_enabled = False
            fields_seeds = {'field': StaticFieldSeed('value')}

        seeder_verbose = DummySeeder(count=1, verbose=True)
        seeder_quiet = DummySeeder(count=1, verbose=False)

        assert seeder_verbose.verbose is True
        assert seeder_quiet.verbose is False