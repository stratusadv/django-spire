import enum

from django.test import TestCase

from django_spire.contrib.seeding import Seeder
from django_spire.contrib.seeding.field.seed.callable_seed import CallableFieldSeed
from django_spire.contrib.seeding.field.seed.random_seed import RandomEnumFieldSeed


class TestRandomFieldSeedHelper(TestCase):
    def test_choice_returns_callable_field_seed(self):
        seq = ['a', 'b', 'c']
        seed = Seeder.random.choice(seq)
        assert isinstance(seed, CallableFieldSeed)
        assert seed.kwargs == {'seq': seq}
        assert seed.generate_value(0) in seq

    def test_choice_generates_from_sequence(self):
        seq = [1, 2, 3]
        seed = Seeder.random.choice(seq)
        value = seed.generate_value(0)
        assert value in seq

    def test_choice_with_empty_sequence(self):
        seq = ['a', 'b']
        seed = Seeder.random.choice(seq)
        result = seed.generate_value(0)
        assert result in seq

    def test_choice_produces_varied_output(self):
        seq = ['a', 'b', 'c', 'd', 'e']
        seed = Seeder.random.choice(seq)
        results = set()
        for _ in range(50):
            results.add(seed.generate_value(0))
        assert len(results) > 1

    def test_enum_returns_random_field_seed(self):
        class Status(enum.Enum):
            PENDING = 'pending'
            ACTIVE = 'active'
            COMPLETED = 'completed'

        seed = Seeder.random.enum(Status)
        assert isinstance(seed, RandomEnumFieldSeed)
        assert seed.enum_ is Status

    def test_enum_generates_enum_value(self):
        class Status(enum.Enum):
            A = 'a'
            B = 'b'
            C = 'c'

        seed = Seeder.random.enum(Status)
        value = seed.generate_value(0)
        assert value in list(Status)

    def test_float_default_range(self):
        seed = Seeder.random.float()
        assert isinstance(seed, CallableFieldSeed)
        assert seed.kwargs == {'a': 0.0, 'b': 1.0}

    def test_float_custom_range(self):
        seed = Seeder.random.float(a=5.0, b=10.0)
        value = seed.generate_value(0)
        assert 5.0 <= value <= 10.0

    def test_float_produces_float_values(self):
        seed = Seeder.random.float()
        value = seed.generate_value(0)
        assert isinstance(value, float)

    def test_float_range_boundaries(self):
        seed = Seeder.random.float(a=0.0, b=0.0)
        value = seed.generate_value(0)
        assert value == 0.0

    def test_int_default_range(self):
        seed = Seeder.random.int()
        assert isinstance(seed, CallableFieldSeed)
        assert seed.kwargs == {'a': 0, 'b': 100}

    def test_int_custom_range(self):
        seed = Seeder.random.int(a=10, b=20)
        value = seed.generate_value(0)
        assert 10 <= value <= 20

    def test_int_produces_int_values(self):
        seed = Seeder.random.int()
        value = seed.generate_value(0)
        assert isinstance(value, int)

    def test_int_range_boundaries(self):
        seed = Seeder.random.int(a=5, b=5)
        value = seed.generate_value(0)
        assert value == 5

    def test_negative_range(self):
        seed = Seeder.random.int(a=-100, b=-50)
        value = seed.generate_value(0)
        assert -100 <= value <= -50

    def test_choice_with_tuples(self):
        seq = [(1, 'a'), (2, 'b')]
        seed = Seeder.random.choice(seq)
        value = seed.generate_value(0)
        assert value in seq

    def test_choice_with_mixed_types(self):
        seq = [1, 'two', 3.0, True]
        seed = Seeder.random.choice(seq)
        value = seed.generate_value(0)
        assert value in seq