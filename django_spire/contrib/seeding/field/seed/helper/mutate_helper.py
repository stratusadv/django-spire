from typing import Callable

from django_spire.contrib.seeding.field.seed.base import BaseFieldSeed
from django_spire.contrib.seeding.field.seed.helper.helper import FieldSeedHelper
from django_spire.contrib.seeding.field.seed.mutate_seed import MutateFieldSeed


class MutateFieldSeedHelper(FieldSeedHelper):
    @staticmethod
    def nullable(
        seed: BaseFieldSeed, null_chance: float, null_value: None = None
    ) -> MutateFieldSeed:
        pass
