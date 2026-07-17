import random
from typing import Any, Callable

from django_spire.contrib.seeding.field.seed.base import BaseFieldSeed


class TransformMutateFieldSeed(BaseFieldSeed):
    def __init__(
        self, field_seed: BaseFieldSeed, transform: Callable, change_chance: float = 0.5
    ) -> None:
        self.field_seed = field_seed
        self.transform = transform
        self.change_chance = change_chance

    def generate_value(self, seed_index: int) -> Any:
        value = self.field_seed.generate_value(seed_index=seed_index)

        if random.random() < self.change_chance:
            return self.transform(value)

        return value


class TypeCoercionMutateFieldSeed(BaseFieldSeed):
    def __init__(
        self, field_seed: BaseFieldSeed, target_type: type, change_chance: float = 0.5
    ) -> None:
        self.field_seed = field_seed
        self.target_type = target_type
        self.change_chance = change_chance

    def generate_value(self, seed_index: int) -> Any:
        value = self.field_seed.generate_value(seed_index=seed_index)

        if random.random() < self.change_chance:
            return self.target_type(value)

        return value
