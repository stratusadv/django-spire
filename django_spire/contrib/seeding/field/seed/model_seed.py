import random
from abc import ABC
from typing import Any

from django.db.models import QuerySet

from django_spire.contrib.seeding.field.seed.base import BaseFieldSeed
from django_spire.contrib.seeding.field.seed.tools import resolve_ordered_index


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

    def generate_cache_key(self) -> str:
        params = getattr(self.queryset.query, 'params', None)
        return f'{self.queryset.model._meta.label}:{self.queryset_key}:{params}'


class OrderedForeignKeyModelFieldSeed(BaseForeignKeyModelFieldSeed):
    def __init__(self, queryset: QuerySet, wrap: bool = False) -> None:
        super().__init__(queryset=queryset)
        self.wrap = wrap

    def generate_cache_key(self) -> str:
        return f'{super().generate_cache_key()}:{self.wrap}'

    def generate_value(self, seed_index: int) -> Any:
        foreign_keys = self.model_foreign_keys(seed_index)
        index = resolve_ordered_index(seed_index, len(foreign_keys), self.wrap, 'foreign keys')
        return foreign_keys[index]


class RandomForeignKeyModelFieldSeed(BaseForeignKeyModelFieldSeed):
    def generate_value(self, seed_index: int) -> Any:
        return random.choice(self.model_foreign_keys(seed_index))
