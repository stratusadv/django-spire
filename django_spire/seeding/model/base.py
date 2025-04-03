from abc import ABC, abstractmethod, ABCMeta

from dandy.recorder import recorder_to_html
from dandy.cache import SqliteCache
from dandy.cache.utils import generate_hash_key

from django_spire.seeding.field.cleaners import normalize_seeder_fields
from django_spire.seeding.model.enums import ModelSeederDefaultsEnum


class ModelSeederMeta(ABCMeta):
    def __new__(cls, name, bases, dct):
        seeder_class = super().__new__(cls, name, bases, dct)

        print(seeder_class.__name__)

        seeder_class._raw_fields = dct.get("fields") or {}
        seeder_class._excluded_fields = {
            k for k, v in seeder_class._raw_fields.items()
            if v == "exclude" or v == ("exclude",)
        }

        seeder_class.fields = normalize_seeder_fields(seeder_class._raw_fields)

        if seeder_class.fields:
            seeder_class._validate_fields_exist(seeder_class.fields)
            seeder_class._assign_default_fields()

        return seeder_class


class BaseModelSeeder(ABC, metaclass=ModelSeederMeta):
    model_class = None
    fields: dict = None
    default_to = "llm"

    cache_name = 'model_seeder'
    cache_limit = 1000

    _field_seeders = []

    @classmethod
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

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
    def _validate_fields_exist(cls, fields: dict):
        field_names = {name for name in cls.field_names()}
        unknown = set(fields.keys()) - field_names

        if unknown:
            raise ValueError(f"Invalid field name(s): {', '.join(unknown)}")

    @classmethod
    def _assign_default_fields(cls):
        if cls.default_to not in ModelSeederDefaultsEnum._value2member_map_:
            raise ValueError(
                f"Invalid default_to value '{cls.default_to}'. Must be one of: {', '.join([v.value for v in SeederDefaultToEnum])}")

        if cls.default_to == ModelSeederDefaultsEnum.INCLUDED:
            return

        method = cls.default_to.lower()
        default_fields = [
            name for name in cls.field_names()
            if name not in cls.fields and name not in cls._excluded_fields
        ]
        cls.fields.update({field_name: (method,) for field_name in default_fields})

    @classmethod
    @recorder_to_html('model_seeder')
    def seed_data(
            cls,
            count=1,
            fields: dict | None = None,
    ) -> list[dict]:

        original_fields = cls.fields.copy()

        if fields:
            cls.fields = {**original_fields, **fields}

        cache = SqliteCache(cache_name=cls.cache_name, limit=cls.cache_limit)
        hash_key = generate_hash_key(cls.seed_data, count=count, fields=fields)
        formatted_seed_data = cache.get(hash_key)

        if formatted_seed_data:
            return formatted_seed_data

        seed_data = []

        for seeder_cls in cls._field_seeders:
            seeder = seeder_cls(cls.fields, cls.default_to)

            if len(seeder.seeder_fields) > 0:
                seed_data.append(seeder.seed(cls, count))

        formatted_seed_data = [dict() for _ in range(max(len(sublist) for sublist in seed_data))]
        for sublist in seed_data:
            for i, d in enumerate(sublist):
                formatted_seed_data[i].update(d)

        cls.fields = original_fields

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
