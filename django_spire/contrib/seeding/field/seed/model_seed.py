import random
from abc import ABC
from typing import Any

from django.db.models import QuerySet

from django_spire.contrib.seeding.field.seed.base import BaseFieldSeed


class BaseForeignKeyModelFieldSeed(BaseFieldSeed, ABC):
    _model_foreign_keys: dict[str, list | None] = {}

    def __init__(self, queryset: QuerySet) -> None:
        self.queryset = queryset
        self.queryset_key = str(queryset.query)

    def model_foreign_keys(self, seed_index: int) -> list:
        if self.__class__._model_foreign_keys.get(self.queryset_key) is None or seed_index == 0:
            self.__class__._model_foreign_keys[self.queryset_key] = list(
                self.queryset.values_list('id', flat=True)
            )

        return self.__class__._model_foreign_keys[self.queryset_key]


class OrderedForeignKeyModelFieldSeed(BaseForeignKeyModelFieldSeed):
    def generate_value(self, seed_index: int) -> Any:
        return self.model_foreign_keys(seed_index)[seed_index]


class RandomForeignKeyModelFieldSeed(BaseForeignKeyModelFieldSeed):
    def generate_value(self, seed_index: int) -> Any:
        return random.choice(self.model_foreign_keys(seed_index))
