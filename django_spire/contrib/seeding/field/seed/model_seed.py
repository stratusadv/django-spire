from typing import Any

from django.db import models
from django.db.models import QuerySet

from django_spire.contrib.seeding.field.seed.base import BaseFieldSeed


class OrderedForeignKeyModelFieldSeed(BaseFieldSeed):
    model_foreign_keys: list | None = None

    def __init__(self, queryset: QuerySet) -> None:
        self.queryset = queryset
        self.__class__.model_foreign_keys = None

    def generate_value(self, seed_index: int) -> Any:
        if self.__class__.model_foreign_keys is None:
            self.__class__.model_foreign_keys = list(
                self.queryset.values_list('id', flat=True)
            )

        return self.__class__.model_foreign_keys[seed_index]
