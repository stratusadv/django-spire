from datetime import UTC, datetime, timedelta
from typing import Any

import pytest
from django.test import TestCase

from django_spire.contrib.seeding.exceptions import DjangoSpireSeederError
from django_spire.contrib.seeding.field.seed.ordered_seed import (
    DateStepFieldSeed,
    OrderedSequenceFieldSeed,
)


class TestOrderedSequenceFieldSeed(TestCase):
    def test_init_stores_sequence(self):
        seed = OrderedSequenceFieldSeed(sequence=['a', 'b', 'c'])
        assert seed.sequence == ['a', 'b', 'c']
        assert seed.wrap is False

    def test_init_with_wrap_true(self):
        seed = OrderedSequenceFieldSeed(sequence=['a', 'b', 'c'], wrap=True)
        assert seed.wrap is True

    def test_init_converts_sequence_to_list(self):
        seed = OrderedSequenceFieldSeed(sequence=('a', 'b'))
        assert seed.sequence == ['a', 'b']

    def test_init_with_empty_sequence_raises_value_error(self):
        with pytest.raises(ValueError, match='requires a non-empty sequence'):
            OrderedSequenceFieldSeed(sequence=[])

    def test_generate_value_returns_values_in_order(self):
        seed = OrderedSequenceFieldSeed(sequence=['a', 'b', 'c'])
        assert seed.generate_value(0) == 'a'
        assert seed.generate_value(1) == 'b'
        assert seed.generate_value(2) == 'c'

    def test_generate_value_out_of_range_raises_seeder_error(self):
        seed = OrderedSequenceFieldSeed(sequence=['a', 'b'])
        with pytest.raises(DjangoSpireSeederError):
            seed.generate_value(2)

    def test_generate_value_with_wrap_cycles(self):
        seed = OrderedSequenceFieldSeed(sequence=['a', 'b', 'c'], wrap=True)
        assert seed.generate_value(0) == 'a'
        assert seed.generate_value(1) == 'b'
        assert seed.generate_value(2) == 'c'
        assert seed.generate_value(3) == 'a'
        assert seed.generate_value(4) == 'b'

    def test_generate_value_single_element_with_wrap(self):
        seed = OrderedSequenceFieldSeed(sequence=['only'], wrap=True)
        for index in range(5):
            assert seed.generate_value(index) == 'only'

    def test_generate_value_with_mixed_types(self):
        sequence: list[Any] = [1, 'two', 3.0]
        seed = OrderedSequenceFieldSeed(sequence=sequence, wrap=True)
        assert seed.generate_value(0) == 1
        assert seed.generate_value(1) == 'two'
        assert seed.generate_value(2) == 3.0
        assert seed.generate_value(3) == 1


class TestDateStepFieldSeed(TestCase):
    def test_init_stores_start_and_step(self):
        start = datetime(2026, 1, 1, tzinfo=UTC)
        step = timedelta(days=1)
        seed = DateStepFieldSeed(start=start, step=step)
        assert seed.start == start
        assert seed.step == step

    def test_generate_value_steps_from_start(self):
        seed = DateStepFieldSeed(start=datetime(2026, 1, 1, tzinfo=UTC), step=timedelta(days=1))
        assert seed.generate_value(0) == datetime(2026, 1, 1, tzinfo=UTC)
        assert seed.generate_value(1) == datetime(2026, 1, 2, tzinfo=UTC)
        assert seed.generate_value(2) == datetime(2026, 1, 3, tzinfo=UTC)

    def test_generate_value_with_hour_step(self):
        seed = DateStepFieldSeed(
            start=datetime(2026, 1, 1, 9, 0, tzinfo=UTC), step=timedelta(hours=6)
        )
        assert seed.generate_value(0) == datetime(2026, 1, 1, 9, 0, tzinfo=UTC)
        assert seed.generate_value(1) == datetime(2026, 1, 1, 15, 0, tzinfo=UTC)
        assert seed.generate_value(2) == datetime(2026, 1, 1, 21, 0, tzinfo=UTC)
        assert seed.generate_value(3) == datetime(2026, 1, 2, 3, 0, tzinfo=UTC)

    def test_generate_value_is_unbounded(self):
        seed = DateStepFieldSeed(start=datetime(2026, 1, 1, tzinfo=UTC), step=timedelta(days=1))
        expected = datetime(2026, 1, 1, tzinfo=UTC) + timedelta(days=1000)
        assert seed.generate_value(1000) == expected
