from django.test import TestCase

from django_spire.contrib.seeding.field.seed.mutate.transform_seed import TypeCoercionMutateFieldSeed
from django_spire.contrib.seeding.field.seed.static_seed import StaticFieldSeed


class TestTypeCoercionMutateFieldSeed(TestCase):
    def test_init_stores_field_seed(self):
        wrapped = StaticFieldSeed('123')
        seed = TypeCoercionMutateFieldSeed(field_seed=wrapped, target_type=int, change_chance=0.5)
        assert seed.field_seed is wrapped

    def test_init_stores_target_type(self):
        wrapped = StaticFieldSeed('123')
        seed = TypeCoercionMutateFieldSeed(field_seed=wrapped, target_type=int, change_chance=0.5)
        assert seed.target_type is int

    def test_init_stores_change_chance(self):
        wrapped = StaticFieldSeed('value')
        seed = TypeCoercionMutateFieldSeed(field_seed=wrapped, target_type=str, change_chance=0.8)
        assert seed.change_chance == 0.8

    def test_default_change_chance(self):
        wrapped = StaticFieldSeed('123')
        seed = TypeCoercionMutateFieldSeed(field_seed=wrapped, target_type=int)
        assert seed.change_chance == 0.5

    def test_coerces_to_int(self):
        wrapped = StaticFieldSeed('123')
        seed = TypeCoercionMutateFieldSeed(field_seed=wrapped, target_type=int, change_chance=1.0)
        assert seed.generate_value(0) == 123
        assert isinstance(seed.generate_value(0), int)

    def test_coerces_to_str(self):
        wrapped = StaticFieldSeed(999)
        seed = TypeCoercionMutateFieldSeed(field_seed=wrapped, target_type=str, change_chance=1.0)
        assert seed.generate_value(0) == '999'
        assert isinstance(seed.generate_value(0), str)

    def test_coerces_to_float(self):
        wrapped = StaticFieldSeed('3.14')
        seed = TypeCoercionMutateFieldSeed(field_seed=wrapped, target_type=float, change_chance=1.0)
        assert seed.generate_value(0) == 3.14
        assert isinstance(seed.generate_value(0), float)

    def test_handles_none_gracefully(self):
        wrapped = StaticFieldSeed(None)
        seed = TypeCoercionMutateFieldSeed(field_seed=wrapped, target_type=str, change_chance=1.0)
        result = seed.generate_value(0)
        assert result is None or isinstance(result, str)

    def test_zero_change_chance_returns_original(self):
        wrapped = StaticFieldSeed('42')
        seed = TypeCoercionMutateFieldSeed(field_seed=wrapped, target_type=int, change_chance=0.0)
        for _ in range(10):
            result = seed.generate_value(0)
            assert result == '42'
            assert isinstance(result, str)

    def test_one_change_chance_always_coerces(self):
        wrapped = StaticFieldSeed('99')
        seed = TypeCoercionMutateFieldSeed(field_seed=wrapped, target_type=int, change_chance=1.0)
        for _ in range(10):
            assert seed.generate_value(0) == 99
            assert isinstance(seed.generate_value(0), int)

    def test_generate_value_passes_seed_index(self):
        wrapped = StaticFieldSeed(42)
        seed = TypeCoercionMutateFieldSeed(field_seed=wrapped, target_type=str, change_chance=1.0)
        for idx in range(3):
            result = seed.generate_value(idx)
            assert result == '42'
            assert isinstance(result, str)

    def test_coerces_negative_number(self):
        wrapped = StaticFieldSeed('-100')
        seed = TypeCoercionMutateFieldSeed(field_seed=wrapped, target_type=int, change_chance=1.0)
        assert seed.generate_value(0) == -100

    def test_coerces_string_int(self):
        wrapped = StaticFieldSeed('42')
        seed = TypeCoercionMutateFieldSeed(field_seed=wrapped, target_type=int, change_chance=1.0)
        result = seed.generate_value(0)
        assert isinstance(result, int)
        assert result == 42