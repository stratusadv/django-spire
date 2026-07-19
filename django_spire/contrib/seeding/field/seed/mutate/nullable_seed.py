import random
from typing import Any

from django_spire.contrib.seeding.field.seed.base import BaseFieldSeed
from django_spire.contrib.seeding.field.seed.mutate.base import BaseMutateFieldSeed


class NullableMutateFieldSeed(BaseMutateFieldSeed):
    def __init__(self, field_seed: BaseFieldSeed, nullify_chance: float = 0.5) -> None:
        self.field_seed = field_seed
        self.nullify_chance = nullify_chance

    def _mutate_value(self, seed_index: int) -> Any:
        if random.random() < self.nullify_chance:
            return None

        return self.field_seed.generate_value(seed_index=seed_index)


