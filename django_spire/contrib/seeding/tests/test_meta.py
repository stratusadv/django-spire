from django.test import TestCase

from django_spire.contrib.seeding import Seeder
from django_spire.contrib.seeding.field.seed.static_seed import StaticFieldSeed
from django_spire.contrib.seeding.meta import SeederMetaData


class TestSeederMetaData(TestCase):
    def test_initial_counters_are_zero(self):
        meta = SeederMetaData()
        assert meta.run_time == 0.0
        assert meta.cached_seed_count == 0
        assert meta.fresh_seed_count == 0

    def test_total_seed_count_sums_cached_and_fresh(self):
        meta = SeederMetaData()
        meta.cached_seed_count = 4
        meta.fresh_seed_count = 6
        assert meta.total_seed_count == 10

    def test_speed_per_seed_divides_run_time_by_total(self):
        meta = SeederMetaData()
        meta.run_time = 2.0
        meta.fresh_seed_count = 4
        assert meta.speed_per_seed == 0.5

    def test_speed_per_seed_verbose_reports_slow(self):
        meta = SeederMetaData()
        meta.run_time = 10.0
        meta.fresh_seed_count = 1
        assert 'Slow' in meta.speed_per_seed_verbose

    def test_speed_per_seed_verbose_reports_good(self):
        meta = SeederMetaData()
        meta.run_time = 0.01
        meta.fresh_seed_count = 1
        assert 'Good' in meta.speed_per_seed_verbose

    def test_speed_per_seed_verbose_reports_acceptable(self):
        meta = SeederMetaData()
        meta.run_time = 0.02
        meta.fresh_seed_count = 1
        assert 'Acceptable' in meta.speed_per_seed_verbose


class TestSeederMeta(TestCase):
    def test_meta_property_returns_class_meta(self):
        class MetaSeeder(Seeder):
            model_class = None
            cache_enabled = False
            fields_seeds = {'name': StaticFieldSeed('Test')}

        seeder = MetaSeeder(count=1, verbose=False)
        assert seeder.meta is MetaSeeder._meta

    def test_seed_increments_fresh_seed_count(self):
        class MetaSeeder(Seeder):
            model_class = None
            cache_enabled = False
            fields_seeds = {'name': StaticFieldSeed('Test')}

        MetaSeeder.reset_meta()
        MetaSeeder(count=3, verbose=False).seed()
        assert MetaSeeder._meta.fresh_seed_count == 3
        assert MetaSeeder._meta.cached_seed_count == 0
        assert MetaSeeder._meta.total_seed_count == 3

    def test_reset_meta_clears_counters(self):
        class MetaSeeder(Seeder):
            model_class = None
            cache_enabled = False
            fields_seeds = {'name': StaticFieldSeed('Test')}

        MetaSeeder(count=2, verbose=False).seed()
        MetaSeeder.reset_meta()
        assert MetaSeeder._meta.total_seed_count == 0
        assert MetaSeeder._meta.run_time == 0.0
