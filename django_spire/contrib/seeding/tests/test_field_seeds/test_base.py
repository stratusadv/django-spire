import pytest
from django.test import TestCase

from django_spire.contrib.seeding.field.seed import callable_seed  # noqa: F401
from django_spire.contrib.seeding.field.seed import exclude_seed  # noqa: F401
from django_spire.contrib.seeding.field.seed import file_seed  # noqa: F401
from django_spire.contrib.seeding.field.seed import index_seed  # noqa: F401
from django_spire.contrib.seeding.field.seed import llm_seed  # noqa: F401
from django_spire.contrib.seeding.field.seed import model_seed  # noqa: F401
from django_spire.contrib.seeding.field.seed import ordered_seed  # noqa: F401
from django_spire.contrib.seeding.field.seed import random_seed  # noqa: F401
from django_spire.contrib.seeding.field.seed.base import BaseFieldSeed
from django_spire.contrib.seeding.field.seed.mutate import corrupt_seed  # noqa: F401
from django_spire.contrib.seeding.field.seed.mutate import exclude_seed as mutate_exclude_seed  # noqa: F401
from django_spire.contrib.seeding.field.seed.mutate import nullable_seed  # noqa: F401
from django_spire.contrib.seeding.field.seed.mutate import transform_seed  # noqa: F401
from django_spire.contrib.seeding.field.seed.static_seed import StaticFieldSeed


def _all_field_seed_subclasses() -> list[type[BaseFieldSeed]]:
    subclasses = []
    pending = [BaseFieldSeed]

    while pending:
        cls = pending.pop(0)

        for subclass in cls.__subclasses__():
            subclasses.append(subclass)
            pending.append(subclass)

    return subclasses


class TestBaseFieldSeedInterface(TestCase):
    def test_is_abstract_class(self):
        with pytest.raises(TypeError):
            BaseFieldSeed()

    def test_static_seed_implements_interface(self):
        seed = StaticFieldSeed('test')
        assert isinstance(seed, BaseFieldSeed)
        assert hasattr(seed, 'generate_value')
        assert callable(seed.generate_value)
        assert hasattr(seed, 'generate_cache_key')
        assert callable(seed.generate_cache_key)
        assert seed.generate_cache_key() == 'test'

    def test_all_concrete_seeds_implement_generate_cache_key(self):
        for subclass in _all_field_seed_subclasses():
            if subclass.__abstractmethods__:
                continue

            seed_cache_key = subclass.generate_cache_key
            assert callable(seed_cache_key)
            assert seed_cache_key is not BaseFieldSeed.generate_cache_key

    def test_static_seed_cache_key_is_stable_for_same_value(self):
        assert (
            StaticFieldSeed('test').generate_cache_key()
            == StaticFieldSeed('test').generate_cache_key()
        )

    def test_static_seed_cache_key_changes_with_value(self):
        assert (
            StaticFieldSeed('one').generate_cache_key()
            != StaticFieldSeed('two').generate_cache_key()
        )

    def test_generate_value_accepts_seed_index(self):
        seed = StaticFieldSeed('test')
        result = seed.generate_value(seed_index=0)
        assert result == 'test'

    def test_generate_value_returns_consistent_value(self):
        seed = StaticFieldSeed(42)
        assert seed.generate_value(0) == 42
        assert seed.generate_value(1) == 42
        assert seed.generate_value(99) == 42
