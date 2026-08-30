from datetime import datetime, timedelta
from typing import Any, Sequence

from django_spire.contrib.seeding.field.seed.base import BaseFieldSeed
from django_spire.contrib.seeding.field.seed.tools import resolve_ordered_index


class OrderedSequenceFieldSeed(BaseFieldSeed):
    def __init__(self, sequence: Sequence, wrap: bool = False) -> None:
        self.sequence = list(sequence)
        self.wrap = wrap

    def generate_cache_key(self) -> str:
        return f'{self.sequence}:{self.wrap}'

    def generate_value(self, seed_index: int) -> Any:
        index = resolve_ordered_index(seed_index, len(self.sequence), self.wrap, 'values')
        return self.sequence[index]


class DateStepFieldSeed(BaseFieldSeed):
    def __init__(self, start: datetime, step: timedelta) -> None:
        self.start = start
        self.step = step

    def generate_cache_key(self) -> str:
        return f'{self.start.isoformat()}:{self.step}'

    def generate_value(self, seed_index: int) -> datetime:
        return self.start + self.step * seed_index
