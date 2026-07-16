from typing import Any

from django_spire.contrib.seeding.field.seed.base import BaseFieldSeed


class OrderedForeignKeyModelFieldSeed(BaseFieldSeed):
    def __init__(self, model_foreign_keys: list[Any]) -> None:
        self.model_foreign_keys = model_foreign_keys

    def generate_value(self, seed_index: int) -> Any:
        return self.model_foreign_keys[seed_index]
