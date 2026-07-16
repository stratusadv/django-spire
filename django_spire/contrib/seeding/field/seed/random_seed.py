import random
from enum import Enum
from typing import Any

from django_spire.contrib.seeding.field.seed.base import BaseFieldSeed


class RandomFieldSeed(BaseFieldSeed):
    def __init__(
        self,
        enum_: Enum | None = None,
    ) -> None:
        self.enum_ = enum_

    def generate_value(self, seed_index: int) -> Any:
        if self.enum_:
            return random.choice(list(self.enum_))

        return None

