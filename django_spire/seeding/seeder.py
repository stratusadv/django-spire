from abc import ABC, abstractmethod

from django_spire.seeding.abc_meta import SeederMeta


class BaseSeeder(ABC, metaclass=SeederMeta):
    keyword: str = None

    seed_keywords = {}

    fields: dict = {}
    default_to: str = "llm"  # 'llm', 'faker', 'included'

    _seeders: list = []
    _original_fields: dict = {}

    @classmethod
    def _normalize_fields(cls, fields: dict) -> dict:
        normalized = {}
        for k, v in fields.items():
            if v == "exclude" or v == ("exclude",):
                continue
            if isinstance(v, tuple):
                normalized[k] = v
            elif callable(v):
                normalized[k] = ("callable", v)
            elif isinstance(v, str) and v.lower() in cls.seed_keywords:
                normalized[k] = (v.lower(),)
            else:
                normalized[k] = ("static", v)
        return normalized

    @classmethod
    def filter_fields(cls, seed_type: str) -> dict:
        return {
            k: v for k, v in cls.fields.items()
            if isinstance(v, tuple) and v[0] == seed_type
        }

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        if cls.keyword is None:
            raise ValueError("Seeds must have a keyword")

    @classmethod
    def seeder_fields(cls):
        return cls.filter_fields(cls.keyword)

    @classmethod
    @abstractmethod
    def seed(cls, model_seeder_cls, count: int):
        pass
