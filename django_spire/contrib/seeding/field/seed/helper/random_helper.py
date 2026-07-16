from enum import Enum
import random
from typing import Sequence

from django_spire.contrib.seeding.field.seed.callable_seed import CallableFieldSeed
from django_spire.contrib.seeding.field.seed.helper.helper import FieldSeedHelper
from django_spire.contrib.seeding.field.seed.random_seed import RandomFieldSeed


class RandomFieldSeedHelper(FieldSeedHelper):
    @staticmethod
    def choice(sequence: Sequence) -> CallableFieldSeed:
        return CallableFieldSeed(random.choice, seq=sequence)

    @staticmethod
    def enum(enum_: Enum) -> RandomFieldSeed:
        return RandomFieldSeed(enum_=enum_)

    @staticmethod
    def float(a: float = 0.0, b: float = 1.0) -> CallableFieldSeed:
        return CallableFieldSeed(random.uniform, a=a, b=b)

    @staticmethod
    def int(a: int = 0, b: int = 100) -> CallableFieldSeed:
        return CallableFieldSeed(random.randint, a=a, b=b)
