from typing import Any

from django_spire.contrib.seeder.field.seed.base import BaseFieldSeed


class StaticFieldSeed(BaseFieldSeed):
    def __init__(self, value: Any) -> None:
        self.value = value

    def generate_value(self) -> Any:
        return self.value
