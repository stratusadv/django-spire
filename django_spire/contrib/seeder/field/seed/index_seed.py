from typing import Any

from django_spire.contrib.seeder.field.seed.base import BaseFieldSeed


class KeyFieldSeed(BaseFieldSeed):
    def __init__(self, keys: list) -> None:
        self.keys = keys

    def generate_value(self) -> Any:
        return None
