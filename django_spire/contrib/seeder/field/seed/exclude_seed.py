from typing import Any

from django_spire.contrib.seeder.field.seed.base import BaseFieldSeed


class ExcludeFieldSeed(BaseFieldSeed):
    def __init__(self) -> None:
        pass

    def generate_value(self) -> Any:
        pass
