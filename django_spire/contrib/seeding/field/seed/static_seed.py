from typing import Any

from django_spire.contrib.seeding.field.seed.base import BaseFieldSeed


class StaticFieldSeed(BaseFieldSeed):
    def __init__(self, value: Any) -> None:
        self.value = value

    def generate_cache_key(self) -> str:
        return str(self.value)

    def generate_value(self, seed_index: int) -> Any:
        _ = seed_index

        return self.value
