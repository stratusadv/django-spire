from typing import Any

from django_spire.contrib.seeding.field.seed.base import BaseFieldSeed


class IndexFieldSeed(BaseFieldSeed):
    def __init__(self, index_start: int = 0, index_step: int = 1) -> None:
        self.index_start = index_start
        self.index_step = index_step

    def generate_value(self, seed_index: int) -> int:
        return (seed_index + self.index_start) * self.index_step
