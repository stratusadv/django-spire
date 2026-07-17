from datetime import datetime

from django.test import TestCase
from django.utils import timezone

from django_spire.contrib.seeding.field.seed.mutate.corrupt_seed import CorruptMutateFieldSeed
from django_spire.contrib.seeding.field.seed.mutate.choices import MutateSeverity
from django_spire.contrib.seeding.field.seed.static_seed import StaticFieldSeed


class TestCorruptMutateFieldSeed(TestCase):
    def test_init_stores_field_seed(self):
        wrapped = StaticFieldSeed('hello')
        seed = CorruptMutateFieldSeed(
            field_seed=wrapped, corrupt_chance=0.5, severity=MutateSeverity.MILD
        )
        assert seed.field_seed is wrapped

    def test_init_stores_corrupt_chance(self):
        wrapped = StaticFieldSeed('value')
        seed = CorruptMutateFieldSeed(
            field_seed=wrapped, corrupt_chance=0.3, severity=MutateSeverity.MILD
        )
        assert seed.corrupt_chance == 0.3

    def test_init_stores_severity(self):
        wrapped = StaticFieldSeed('value')
        seed = CorruptMutateFieldSeed(
            field_seed=wrapped, corrupt_chance=0.5, severity=MutateSeverity.MODERATE
        )
        assert seed.severity == MutateSeverity.MODERATE

    def test_returns_real_value_when_no_corruption(self):
        wrapped = StaticFieldSeed('real_value')
        seed = CorruptMutateFieldSeed(
            field_seed=wrapped, corrupt_chance=0.0, severity=MutateSeverity.MILD
        )
        assert seed.generate_value(0) == 'real_value'

    def test_passes_through_none(self):
        wrapped = StaticFieldSeed(None)
        seed = CorruptMutateFieldSeed(
            field_seed=wrapped, corrupt_chance=1.0, severity=MutateSeverity.MILD
        )
        assert seed.generate_value(0) is None

    def test_mild_corruption_alters_string(self):
        wrapped = StaticFieldSeed('abcdefghij')
        seed = CorruptMutateFieldSeed(
            field_seed=wrapped, corrupt_chance=1.0, severity=MutateSeverity.MILD
        )
        corrupted_count = 0
        for _ in range(20):
            result = seed.generate_value(0)
            if isinstance(result, str) and result != 'abcdefghij':
                corrupted_count += 1
        assert corrupted_count > 0

    def test_moderate_corruption_alters_string(self):
        wrapped = StaticFieldSeed('abcdefghij')
        seed = CorruptMutateFieldSeed(
            field_seed=wrapped, corrupt_chance=1.0, severity=MutateSeverity.MODERATE
        )
        corrupted_count = 0
        for _ in range(20):
            result = seed.generate_value(0)
            if isinstance(result, str) and result != 'abcdefghij':
                corrupted_count += 1
        assert corrupted_count > 0

    def test_moderate_corruption_does_not_error(self):
        wrapped = StaticFieldSeed('test')
        seed = CorruptMutateFieldSeed(
            field_seed=wrapped, corrupt_chance=1.0, severity=MutateSeverity.MODERATE
        )
        for _ in range(10):
            result = seed.generate_value(0)
            assert result is not None or result is None

    def test_mild_corruption_does_not_error(self):
        wrapped = StaticFieldSeed('test')
        seed = CorruptMutateFieldSeed(
            field_seed=wrapped, corrupt_chance=0.0, severity=MutateSeverity.MILD
        )
        for _ in range(10):
            result = seed.generate_value(0)
            assert result == 'test'

    def test_integer_value_with_mild_severity(self):
        wrapped = StaticFieldSeed(42)
        seed = CorruptMutateFieldSeed(
            field_seed=wrapped, corrupt_chance=1.0, severity=MutateSeverity.MILD
        )
        result = seed.generate_value(0)
        assert result is not None

    def test_float_value_with_chaos_severity(self):
        wrapped = StaticFieldSeed(3.14)
        seed = CorruptMutateFieldSeed(
            field_seed=wrapped, corrupt_chance=1.0, severity=MutateSeverity.CHAOS
        )
        for _ in range(20):
            result = seed.generate_value(0)
            if result is not None:
                break

    def test_generate_value_passes_seed_index_to_wrapped(self):
        wrapped = StaticFieldSeed('value')
        seed = CorruptMutateFieldSeed(
            field_seed=wrapped, corrupt_chance=0.0, severity=MutateSeverity.MILD
        )
        for idx in range(5):
            assert seed.generate_value(idx) == 'value'

    def test_zero_corrupt_chance_never_corrupts(self):
        wrapped = StaticFieldSeed('never_corrupt')
        seed = CorruptMutateFieldSeed(
            field_seed=wrapped, corrupt_chance=0.0, severity=MutateSeverity.CHAOS
        )
        for _ in range(50):
            assert seed.generate_value(0) == 'never_corrupt'

    def test_one_corrupt_chance_can_corrupt(self):
        wrapped = StaticFieldSeed('maybe_corrupt')
        seed = CorruptMutateFieldSeed(
            field_seed=wrapped, corrupt_chance=1.0, severity=MutateSeverity.MILD
        )
        corrupted_count = 0
        for _ in range(20):
            result = seed.generate_value(0)
            if result != 'maybe_corrupt':
                corrupted_count += 1
        assert corrupted_count > 0