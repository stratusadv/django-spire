from typing import Callable

from django_spire.contrib.seeder.field.seed.callable_seed import CallableFieldSeed
from django_spire.contrib.seeder.field.seed.helper.helper import FieldSeedHelper


class CustomFieldSeedHelper(FieldSeedHelper):
    @staticmethod
    def callable(callable_: Callable, *args, **kwargs) -> CallableFieldSeed:
        return CallableFieldSeed(callable_, *args, **kwargs)
