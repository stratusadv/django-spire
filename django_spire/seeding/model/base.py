from abc import ABC, abstractmethod

from dandy.recorder import recorder_to_html
from dandy.cache import SqliteCache
from dandy.cache.utils import generate_hash_key

from django_spire.seeding.model.config import FieldsConfig


class BaseModelSeeder(ABC):
    model_class = None

    fields = None
    field_config_class = FieldsConfig

    default_to = "llm"

    cache_name = 'model_seeder'
    cache_limit = 1000

    _field_seeders = []
    _field_config: FieldsConfig = None

    @classmethod
    def get_field_config(cls) -> FieldsConfig:
        if cls._field_config is None:

            if cls.model_class is None:
                raise ValueError("model_class must be defined before using seeder.")

            raw_fields = cls.__dict__.get("fields", {})
            cls._field_config = cls.field_config_class(
                raw_fields=raw_fields,
                field_names=cls.field_names(),
                default_to=cls.default_to,
                model_class=cls.model_class
            )
        return cls._field_config

    @classmethod
    @property
    def resolved_fields(cls):
        return cls.get_field_config().fields

    @classmethod
    def clear_cache(cls):
        SqliteCache(
            cache_name=cls.cache_name,
            limit=cls.cache_limit
        ).clear(cache_name=cls.cache_name)

    @classmethod
    @abstractmethod
    def field_names(cls) -> list[str]:
        pass

    @classmethod
    @recorder_to_html('model_seeder')
    def seed_data(
            cls,
            count=1,
            fields: dict | None = None,
    ) -> list[dict]:

        field_config = cls.get_field_config().override(fields) if fields else cls.get_field_config()

        cache = SqliteCache(cache_name=cls.cache_name, limit=cls.cache_limit)
        hash_key = generate_hash_key(cls.seed_data, count=count, fields=fields)
        formatted_seed_data = cache.get(hash_key)

        if formatted_seed_data:
            return formatted_seed_data

        seed_data = []

        for seeder_cls in cls._field_seeders:
            seeder = seeder_cls(field_config.fields, field_config.default_to)

            if len(seeder.seeder_fields) > 0:
                seed_data.append(seeder.seed(cls, count))

        formatted_seed_data = [dict() for _ in range(max(len(sublist) for sublist in seed_data))]
        for sublist in seed_data:
            for i, d in enumerate(sublist):
                formatted_seed_data[i].update(d)

        cache.set(hash_key, formatted_seed_data)
        return formatted_seed_data

    @classmethod
    def seed(
            cls,
            count: int = 1,
            fields: dict | None = None,
    ) -> list:
        return [
            cls.model_class(**seed_data)
            for seed_data in cls.seed_data(count, fields)
        ]
