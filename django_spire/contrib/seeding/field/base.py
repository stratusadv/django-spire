from abc import ABC, abstractmethod

from django_spire.contrib.seeding.field.cleaners import normalize_seeder_fields
from django_spire.contrib.seeding.field.enums import FieldSeederTypesEnum


class BaseFieldSeeder(ABC):
    keyword: str = None
    seed_keywords = FieldSeederTypesEnum._value2member_map_.keys()

    def __init__(
            self,
            fields: dict = None,
            default_to: str = "llm"
    ):

        self.fields = self._normalize_fields(fields or {})
        self.default_to = default_to


    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        if cls.keyword is None:
            raise ValueError("Seeds must have a keyword")

    def _normalize_fields(self, fields: dict) -> dict:
        return normalize_seeder_fields(fields)

    def filter_fields(self, seed_type: str) -> dict:
        return {
            k: v for k, v in self.fields.items()
            if isinstance(v, tuple) and v[0] == seed_type
        }

    @property
    def seeder_fields(self):
        return self.filter_fields(self.keyword)

    @abstractmethod
    def seed(self, model_seeder_cls, count: int):
        pass
