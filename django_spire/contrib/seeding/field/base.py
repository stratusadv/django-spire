from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from django_spire.contrib.seeding.field.cleaners import normalize_seeder_fields
from django_spire.contrib.seeding.field.enums import FieldSeederTypesEnum

if TYPE_CHECKING:
    from typing import Any


class BaseFieldSeeder(ABC):
    keyword: str = None
    seed_keywords = FieldSeederTypesEnum._value2member_map_.keys()

    def __init__(
        self,
        fields: dict | None = None,
        default_to: str = 'llm'
    ) -> None:

        self.fields = self._normalize_fields(fields or {})
        self.default_to = default_to


    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)

        if cls.keyword is None:
            message = 'Seeds must have a keyword'
            raise ValueError(message)

    def _normalize_fields(self, fields: dict) -> dict:
        return normalize_seeder_fields(fields)

    def filter_fields(self, seed_type: str) -> dict:
        return {
            k: v for k, v in self.fields.items()
            if isinstance(v, tuple) and v[0] == seed_type
        }

    @property
    def seeder_fields(self) -> dict:
        return self.filter_fields(self.keyword)

    @abstractmethod
    def seed(self, model_seeder_cls: Any, count: int) -> list[dict]:
        pass
