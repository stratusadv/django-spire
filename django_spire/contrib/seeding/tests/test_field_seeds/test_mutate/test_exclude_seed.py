from django.test import TestCase

from django_spire.contrib.seeding.field.seed.mutate.exclude_seed import ExcludeMutateFieldSeed
from django_spire.contrib.seeding.field.seed.static_seed import StaticFieldSeed


class TestExcludeMutateFieldSeed(TestCase):
    def test_init_stores_field_seed(self):
        wrapped = StaticFieldSeed('hello')
        seed = ExcludeMutateFieldSeed(field_seed=wrapped, exclude_chance=0.5)
        assert seed.field_seed is wrapped

    def test_init_stores_exclude_chance(self):
        wrapped = StaticFieldSeed('value')
        seed = ExcludeMutateFieldSeed(field_seed=wrapped, exclude_chance=0.3)
        assert seed.exclude_chance == 0.3

    def test_default_exclude_chance(self):
        wrapped = StaticFieldSeed('value')
        seed = ExcludeMutateFieldSeed(field_seed=wrapped)
        assert seed.exclude_chance == 0.5

    def test_generate_cache_key_includes_class_wrapped_key_and_chance(self):
        wrapped = StaticFieldSeed('value')
        seed = ExcludeMutateFieldSeed(field_seed=wrapped, exclude_chance=0.25)
        assert seed.generate_cache_key() == 'ExcludeMutateFieldSeed:value:0.25'

    def test_generate_cache_key_changes_with_chance(self):
        wrapped = StaticFieldSeed('value')
        low = ExcludeMutateFieldSeed(field_seed=wrapped, exclude_chance=0.1)
        high = ExcludeMutateFieldSeed(field_seed=wrapped, exclude_chance=0.9)
        assert low.generate_cache_key() != high.generate_cache_key()

    def test_generate_value_returns_field_seed_not_value(self):
        wrapped = StaticFieldSeed('real_value')
        seed = ExcludeMutateFieldSeed(field_seed=wrapped, exclude_chance=0.0)
        assert seed.generate_value(0) is wrapped

    def test_zero_chance_never_excludes(self):
        wrapped = StaticFieldSeed('never_excluded')
        seed = ExcludeMutateFieldSeed(field_seed=wrapped, exclude_chance=0.0)
        for _ in range(100):
            assert seed.generate_value(0) is wrapped

    def test_one_chance_always_excludes(self):
        wrapped = StaticFieldSeed('always_excluded')
        seed = ExcludeMutateFieldSeed(field_seed=wrapped, exclude_chance=1.0)
        for _ in range(100):
            assert seed.generate_value(0) is None

    def test_generate_value_on_init_index_returns_field_seed(self):
        wrapped = StaticFieldSeed('value')
        seed = ExcludeMutateFieldSeed(field_seed=wrapped, exclude_chance=1.0)
        assert seed.generate_value(-1) is wrapped

    def test_generate_value_passes_seed_index(self):
        wrapped = StaticFieldSeed('value')
        seed = ExcludeMutateFieldSeed(field_seed=wrapped, exclude_chance=0.0)
        for seed_index in range(5):
            assert seed.generate_value(seed_index).generate_value(seed_index) == 'value'
