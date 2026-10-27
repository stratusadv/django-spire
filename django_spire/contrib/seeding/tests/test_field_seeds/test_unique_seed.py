from concurrent.futures import ThreadPoolExecutor
from typing import Any

import pytest
from django.test import TestCase

from django_spire.auth.user.models import AuthUser
from django_spire.contrib.seeding import Seeder
from django_spire.contrib.seeding.exceptions import DjangoSpireSeederError
from django_spire.contrib.seeding.field.seed.ordered_seed import OrderedSequenceFieldSeed
from django_spire.contrib.seeding.field.seed.static_seed import StaticFieldSeed
from django_spire.contrib.seeding.field.seed.unique_seed import UniqueFieldSeed


class TestUniqueFieldSeedInit(TestCase):
    def test_init_with_inner_seed(self):
        inner = StaticFieldSeed('a')
        seed = UniqueFieldSeed(field_seed=inner)
        assert seed.base_seed is inner
        assert seed.base_callable is None

    def test_init_with_callable(self):
        seed = UniqueFieldSeed(row_value_callable=lambda row: row['name'].lower())
        assert seed.base_seed is None
        assert seed.base_callable is not None

    def test_init_with_row_field_name(self):
        seed = UniqueFieldSeed(row_field='email')
        assert seed.base_seed is None
        assert seed.base_callable is not None

    def test_init_without_source_raises(self):
        with pytest.raises(DjangoSpireSeederError):
            UniqueFieldSeed()

    def test_init_with_multiple_sources_raises(self):
        with pytest.raises(DjangoSpireSeederError):
            UniqueFieldSeed(field_seed=StaticFieldSeed('a'), row_field='email')

    def test_is_cache_unsafe(self):
        assert UniqueFieldSeed(field_seed=StaticFieldSeed('a')).is_cache_unsafe is True

    def test_cache_key_is_stable_for_same_inner_seed(self):
        assert (
            UniqueFieldSeed(field_seed=StaticFieldSeed('a')).generate_cache_key()
            == UniqueFieldSeed(field_seed=StaticFieldSeed('a')).generate_cache_key()
        )

    def test_cache_key_changes_with_inner_seed(self):
        assert (
            UniqueFieldSeed(field_seed=StaticFieldSeed('a')).generate_cache_key()
            != UniqueFieldSeed(field_seed=StaticFieldSeed('b')).generate_cache_key()
        )

    def test_cache_key_uses_callable_qualname(self):
        def base_from_row(row: dict[str, Any]) -> str:
            return row['name']

        seed = UniqueFieldSeed(row_value_callable=base_from_row)
        assert seed.generate_cache_key().endswith('.base_from_row')


class TestUniqueFieldSeedBatchOnly(TestCase):
    def test_wrapped_duplicates_get_numeric_suffixes(self):
        seed = UniqueFieldSeed(field_seed=OrderedSequenceFieldSeed(['a', 'b'], wrap=True))
        seed.generate_value(-1)

        values = [seed.generate_value(i) for i in range(5)]

        assert values == ['a', 'b', 'a-2', 'b-2', 'a-3']
        assert len(set(values)) == 5

    def test_single_value_wraps_with_suffixes(self):
        seed = UniqueFieldSeed(field_seed=OrderedSequenceFieldSeed(['only'], wrap=True))
        seed.generate_value(-1)

        values = [seed.generate_value(i) for i in range(3)]

        assert values == ['only', 'only-2', 'only-3']

    def test_init_at_minus_one_resets_state_between_runs(self):
        seed = UniqueFieldSeed(field_seed=OrderedSequenceFieldSeed(['a', 'b'], wrap=True))
        seed.generate_value(-1)

        first_run = [seed.generate_value(i) for i in range(3)]

        seed.generate_value(-1)

        second_run = [seed.generate_value(i) for i in range(3)]

        assert first_run == second_run

    def test_without_init_degrades_to_batch_only(self):
        seed = UniqueFieldSeed(field_seed=OrderedSequenceFieldSeed(['a', 'b'], wrap=True))

        values = [seed.generate_value(i) for i in range(5)]

        assert len(set(values)) == 5

    def test_concurrent_generation_yields_unique_values(self):
        seed = UniqueFieldSeed(field_seed=OrderedSequenceFieldSeed(['a', 'b', 'c'], wrap=True))
        seed.generate_value(-1)

        with ThreadPoolExecutor(max_workers=12) as executor:
            values = list(executor.map(seed.generate_value, range(50)))

        assert len(set(values)) == 50


class TestUniqueFieldSeedWithModel(TestCase):
    def _seed(self) -> UniqueFieldSeed:
        seed = UniqueFieldSeed(field_seed=OrderedSequenceFieldSeed(['a', 'b'], wrap=True))
        seed.generate_value_context(-1, model_class=AuthUser, field_name='username')

        return seed

    def test_db_snapshot_skips_existing_values(self):
        AuthUser.objects.create(username='a')
        seed = self._seed()

        values = [seed.generate_value(i) for i in range(4)]

        assert values == ['a-2', 'b', 'a-3', 'b-2']

    def test_db_snapshot_refreshes_between_runs(self):
        AuthUser.objects.create(username='a')
        seed = self._seed()

        assert seed.generate_value(0) == 'a-2'
        assert seed.generate_value(1) == 'b'

        AuthUser.objects.create(username='b')

        seed.generate_value_context(-1, model_class=AuthUser, field_name='username')

        assert seed.generate_value(0) == 'a-2'
        assert seed.generate_value(1) == 'b-2'

    def test_truncates_to_field_max_length(self):
        seed = UniqueFieldSeed(field_seed=StaticFieldSeed('x' * 200))
        seed.generate_value_context(-1, model_class=AuthUser, field_name='username')

        values = [seed.generate_value(i) for i in range(2)]

        assert all(len(value) == 150 for value in values)
        assert values[1] == 'x' * 148 + '-2'

    def test_callable_receives_partial_row_values(self):
        seen_rows = []

        def base_from_row(row: dict[str, Any]) -> str:
            seen_rows.append(dict(row))
            return row['name'].lower()

        seed = UniqueFieldSeed(row_value_callable=base_from_row)
        seed.generate_value_context(
            0,
            model_class=AuthUser,
            field_name='username',
            row_values={'name': 'Sales', 'description': 'Sales desk'},
        )

        assert seen_rows == [{'name': 'Sales', 'description': 'Sales desk'}]

    def test_callable_row_values_are_copied(self):
        seed = UniqueFieldSeed(row_value_callable=lambda row: row['name'])
        seed.generate_value(-1)

        row = {'name': 'Sales'}
        first = seed.generate_value_context(1, row_values=row)
        row['name'] = 'Mutated'

        assert first == 'Sales'

    def test_row_field_name_copies_field_value(self):
        seed = UniqueFieldSeed(row_field='email')
        seed.generate_value(-1)

        first = seed.generate_value_context(0, row_values={'email': 'a@example.com'})
        second = seed.generate_value_context(1, row_values={'email': 'a@example.com'})
        third = seed.generate_value_context(2, row_values={'email': 'b@example.com'})

        assert first == 'a@example.com'
        assert second == 'a@example.com-2'
        assert third == 'b@example.com'


class TestSeederUniqueApi(TestCase):
    def test_unique_with_inner_seed(self):
        seed = Seeder.unique(field_seed=Seeder.ordered.choice(['a', 'b'], wrap=True))
        assert isinstance(seed, UniqueFieldSeed)

    def test_unique_with_callable(self):
        seed = Seeder.unique(row_value_callable=lambda row: row['name'])
        assert isinstance(seed, UniqueFieldSeed)

    def test_unique_with_row_field_name(self):
        seed = Seeder.unique(row_field='email')

        assert isinstance(seed, UniqueFieldSeed)
        value = seed.generate_value_context(0, row_values={'email': 'a@example.com'})
        assert value == 'a@example.com'
