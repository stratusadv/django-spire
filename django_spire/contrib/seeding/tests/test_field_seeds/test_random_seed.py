import enum

from django.test import TestCase

from django_spire.contrib.seeding.field.seed.random_seed import RandomEnumFieldSeed


class TestRandomFieldSeed(TestCase):
    def test_returns_random_enum_member(self):
        class Status(enum.Enum):
            PENDING = 'pending'
            ACTIVE = 'active'
            COMPLETED = 'completed'

        seed = RandomEnumFieldSeed(enum_=Status)
        value = seed.generate_value(0)
        assert value in list(Status)

    def test_returns_none_without_enum(self):
        seed = RandomEnumFieldSeed()
        assert seed.generate_value(0) is None

    def test_stores_enum_attribute(self):
        class Status(enum.Enum):
            ACTIVE = 'active'

        seed = RandomEnumFieldSeed(enum_=Status)
        assert seed.enum_ is Status

    def test_enum_with_two_members(self):
        class Binary(enum.Enum):
            ZERO = 0
            ONE = 1

        seed = RandomEnumFieldSeed(enum_=Binary)
        value = seed.generate_value(0)
        assert value in [Binary.ZERO, Binary.ONE]

    def test_produces_varied_output(self):
        class Status(enum.Enum):
            A = 'a'
            B = 'b'
            C = 'c'

        seed = RandomEnumFieldSeed(enum_=Status)
        results = set()
        for _ in range(100):
            results.add(seed.generate_value(0))
        assert len(results) > 1

    def test_seed_index_does_not_affect_result(self):
        class Status(enum.Enum):
            ACTIVE = 'active'

        seed = RandomEnumFieldSeed(enum_=Status)
        for i in range(10):
            assert seed.generate_value(i) == Status.ACTIVE