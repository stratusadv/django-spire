from datetime import UTC, datetime, timedelta

from django.test import TestCase
from django.utils import timezone

from django_spire.contrib.seeding import Seeder
from django_spire.contrib.seeding.field.seed.ordered_seed import (
    DateStepFieldSeed,
    OrderedSequenceFieldSeed,
)


class TestOrderedFieldSeedHelper(TestCase):
    def test_choice_returns_ordered_sequence_field_seed(self):
        seq = ['a', 'b', 'c']
        seed = Seeder.ordered.choice(seq)
        assert isinstance(seed, OrderedSequenceFieldSeed)
        assert seed.sequence == seq
        assert seed.wrap is False

    def test_choice_with_wrap_true(self):
        seed = Seeder.ordered.choice(['a', 'b'], wrap=True)
        assert isinstance(seed, OrderedSequenceFieldSeed)
        assert seed.wrap is True

    def test_choice_with_wrap_cycles(self):
        seed = Seeder.ordered.choice(['a', 'b', 'c'], wrap=True)
        values = [seed.generate_value(index) for index in range(5)]
        assert values == ['a', 'b', 'c', 'a', 'b']

    def test_choice_without_wrap_generates_in_order(self):
        seed = Seeder.ordered.choice(['a', 'b'])
        assert seed.generate_value(0) == 'a'
        assert seed.generate_value(1) == 'b'

    def test_datetime_returns_date_step_field_seed(self):
        start = datetime(2026, 1, 1, tzinfo=UTC)
        step = timedelta(days=1)
        seed = Seeder.ordered.datetime(start=start, step=step)
        assert isinstance(seed, DateStepFieldSeed)

    def test_datetime_makes_naive_start_aware(self):
        start = datetime(2026, 1, 1, tzinfo=UTC).replace(tzinfo=None)
        seed = Seeder.ordered.datetime(start=start, step=timedelta(days=1))
        assert timezone.is_aware(seed.start)

    def test_datetime_keeps_aware_start(self):
        start = datetime(2026, 1, 1, tzinfo=UTC)
        seed = Seeder.ordered.datetime(start=start, step=timedelta(days=1))
        assert seed.start == start

    def test_datetime_generates_stepping_values(self):
        seed = Seeder.ordered.datetime(
            start=datetime(2026, 1, 1, tzinfo=UTC), step=timedelta(days=2)
        )
        assert seed.generate_value(0) == datetime(2026, 1, 1, tzinfo=UTC)
        assert seed.generate_value(1) == datetime(2026, 1, 3, tzinfo=UTC)
        assert seed.generate_value(2) == datetime(2026, 1, 5, tzinfo=UTC)
