from datetime import datetime, timedelta
from typing import Sequence

from django.utils import timezone

from django_spire.contrib.seeding.field.seed.helper.helper import FieldSeedHelper
from django_spire.contrib.seeding.field.seed.ordered_seed import (
    DateStepFieldSeed,
    OrderedSequenceFieldSeed,
)


class OrderedFieldSeedHelper(FieldSeedHelper):
    @staticmethod
    def choice(sequence: Sequence, wrap: bool = False) -> OrderedSequenceFieldSeed:
        return OrderedSequenceFieldSeed(sequence=sequence, wrap=wrap)

    @staticmethod
    def datetime(start: datetime, step: timedelta) -> DateStepFieldSeed:
        if timezone.is_naive(start):
            start = timezone.make_aware(start)

        return DateStepFieldSeed(start=start, step=step)
