import pytest
from django.test import TestCase

from django_spire.contrib.seeding.field.seed.base import BaseFieldSeed
from django_spire.contrib.seeding.field.seed.static_seed import StaticFieldSeed


class TestBaseFieldSeedInterface(TestCase):
    def test_is_abstract_class(self):
        with pytest.raises(TypeError):
            BaseFieldSeed()

    def test_static_seed_implements_interface(self):
        seed = StaticFieldSeed('test')
        assert isinstance(seed, BaseFieldSeed)
        assert hasattr(seed, 'generate_value')
        assert callable(seed.generate_value)

    def test_generate_value_accepts_seed_index(self):
        seed = StaticFieldSeed('test')
        result = seed.generate_value(seed_index=0)
        assert result == 'test'

    def test_generate_value_returns_consistent_value(self):
        seed = StaticFieldSeed(42)
        assert seed.generate_value(0) == 42
        assert seed.generate_value(1) == 42
        assert seed.generate_value(99) == 42