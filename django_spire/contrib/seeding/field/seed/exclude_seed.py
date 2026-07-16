from typing import Any

from django_spire.contrib.seeding.field.seed.base import BaseFieldSeed


class ExcludeFieldSeed(BaseFieldSeed):
    def __init__(self) -> None:
        pass

    def generate_value(self, seed_index: int) -> Any:
        pass
