import random
from typing import Any

from django_spire.contrib.seeding.field.seed.base import BaseFieldSeed


class ExcludeMutateFieldSeed(BaseFieldSeed):
    def __init__(self, field_seed: BaseFieldSeed, exclude_chance: float = 0.5) -> None:
        self.field_seed = field_seed
        self.exclude_chance = exclude_chance

    def generate_value(self, seed_index: int) -> BaseFieldSeed | None:
        _ = seed_index
        
        if random.random() < self.exclude_chance:
            return None

        return self.field_seed


