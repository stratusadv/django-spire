from django.test import TestCase

from django_spire.contrib.seeding.field.seed.mutate.nullable_seed import NullableMutateFieldSeed
from django_spire.contrib.seeding.field.seed.static_seed import StaticFieldSeed


class TestNullableMutateFieldSeed(TestCase):
    def test_init_stores_field_seed(self):
        wrapped = StaticFieldSeed('hello')
        seed = NullableMutateFieldSeed(field_seed=wrapped, nullify_chance=0.5)
        assert seed.field_seed is wrapped

    def test_init_stores_nullify_chance(self):
        wrapped = StaticFieldSeed('value')
        seed = NullableMutateFieldSeed(field_seed=wrapped, nullify_chance=0.3)
        assert seed.nullify_chance == 0.3

    def test_default_nullify_chance(self):
        wrapped = StaticFieldSeed('value')
        seed = NullableMutateFieldSeed(field_seed=wrapped)
        assert seed.nullify_chance == 0.5

    def test_generate_value_returns_wrapped_value_when_not_null(self):
        wrapped = StaticFieldSeed('real_value')
        seed = NullableMutateFieldSeed(field_seed=wrapped, nullify_chance=0.0)
        assert seed.generate_value(0) == 'real_value'

    def test_generate_value_can_return_none(self):
        wrapped = StaticFieldSeed('value')
        seed = NullableMutateFieldSeed(field_seed=wrapped, nullify_chance=1.0)
        assert seed.generate_value(0) is None

    def test_generate_value_passes_seed_index(self):
        wrapped = StaticFieldSeed('value')
        seed = NullableMutateFieldSeed(field_seed=wrapped, nullify_chance=0.0)
        for idx in range(5):
            assert seed.generate_value(idx) == 'value'

    def test_zero_chance_returns_wrapped(self):
        wrapped = StaticFieldSeed('never_null')
        seed = NullableMutateFieldSeed(field_seed=wrapped, nullify_chance=0.0)
        for _ in range(100):
            assert seed.generate_value(0) == 'never_null'

    def test_one_chance_returns_none(self):
        wrapped = StaticFieldSeed('always_null')
        seed = NullableMutateFieldSeed(field_seed=wrapped, nullify_chance=1.0)
        for _ in range(10):
            assert seed.generate_value(0) is None