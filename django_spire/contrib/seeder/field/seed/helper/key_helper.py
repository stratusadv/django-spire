from typing import Any

from django_spire.contrib.seeder.field.seed.helper.helper import FieldSeedHelper
from django_spire.contrib.seeder.field.seed.index_seed import KeyFieldSeed


class KeyFieldSeedHelper(FieldSeedHelper):
    @staticmethod
    def in_order(keys: list[Any]) -> KeyFieldSeed:
        return KeyFieldSeed(keys=keys)

