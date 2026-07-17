import random
from abc import ABC
from typing import Any

from django.db.models import QuerySet

from django_spire.contrib.seeding.field.seed.base import BaseFieldSeed


class BaseForeignKeyModelFieldSeed(BaseFieldSeed, ABC):
    model_foreign_keys: list | None = None

    def __init__(self, queryset: QuerySet) -> None:
        self.queryset = queryset
        self.__class__.model_foreign_keys = None

    def _load_foreign_keys(self) -> None:
        if self.__class__.model_foreign_keys is None:
            self.__class__.model_foreign_keys = list(self.queryset.values_list('id', flat=True))


class OrderedForeignKeyModelFieldSeed(BaseForeignKeyModelFieldSeed):
    def generate_value(self, seed_index: int) -> Any:
        self._load_foreign_keys()

        return self.__class__.model_foreign_keys[seed_index]


class RandomForeignKeyModelFieldSeed(BaseForeignKeyModelFieldSeed):
    def generate_value(self, seed_index: int) -> Any:
        _ = seed_index
        self._load_foreign_keys()

        return random.choice(self.__class__.model_foreign_keys)
