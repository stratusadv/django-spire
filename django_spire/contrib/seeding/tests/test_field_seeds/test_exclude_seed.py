from django.test import TestCase

from django_spire.contrib.seeding.field.seed.exclude_seed import ExcludeFieldSeed


class TestExcludeFieldSeed(TestCase):
    def test_generate_value_returns_none(self):
        seed = ExcludeFieldSeed()
        assert seed.generate_value(0) is None

    def test_generate_value_returns_none_for_any_index(self):
        seed = ExcludeFieldSeed()
        for i in range(10):
            assert seed.generate_value(i) is None

    def test_seed_is_instantiable(self):
        seed = ExcludeFieldSeed()
        assert seed is not None