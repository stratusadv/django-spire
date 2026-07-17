import enum

from django.test import TestCase

from django_spire.contrib.seeding.field.seed.static_seed import StaticFieldSeed


class TestStaticFieldSeed(TestCase):
    def test_returns_string_value(self):
        seed = StaticFieldSeed('hello')
        assert seed.generate_value(0) == 'hello'

    def test_returns_int_value(self):
        seed = StaticFieldSeed(42)
        assert seed.generate_value(0) == 42

    def test_returns_bool_true(self):
        seed = StaticFieldSeed(True)
        assert seed.generate_value(0) is True

    def test_returns_bool_false(self):
        seed = StaticFieldSeed(False)
        assert seed.generate_value(0) is False

    def test_returns_list(self):
        seed = StaticFieldSeed([1, 2, 3])
        assert seed.generate_value(0) == [1, 2, 3]

    def test_returns_dict(self):
        seed = StaticFieldSeed({'key': 'value'})
        assert seed.generate_value(0) == {'key': 'value'}

    def test_returns_none(self):
        seed = StaticFieldSeed(None)
        assert seed.generate_value(0) is None

    def test_returns_empty_string(self):
        seed = StaticFieldSeed('')
        assert seed.generate_value(0) == ''

    def test_returns_empty_list(self):
        seed = StaticFieldSeed([])
        assert seed.generate_value(0) == []

    def test_returns_zero(self):
        seed = StaticFieldSeed(0)
        assert seed.generate_value(0) == 0

    def test_returns_float(self):
        seed = StaticFieldSeed(3.14)
        assert seed.generate_value(0) == 3.14

    def test_returns_tuple(self):
        seed = StaticFieldSeed((1, 2, 3))
        assert seed.generate_value(0) == (1, 2, 3)

    def test_returns_enum(self):
        class Status(enum.Enum):
            ACTIVE = 'active'

        seed = StaticFieldSeed(Status.ACTIVE)
        assert seed.generate_value(0) == Status.ACTIVE

    def test_returns_value_independently_of_seed_index(self):
        seed = StaticFieldSeed('constant')
        for i in range(100):
            assert seed.generate_value(i) == 'constant'

    def test_stores_value_attribute(self):
        seed = StaticFieldSeed('stored_value')
        assert seed.value == 'stored_value'