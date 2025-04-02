from abc import ABC, abstractmethod, ABCMeta

from django_spire.seeding.field.cleaners import normalize_seeder_fields
from django_spire.seeding.model.enums import ModelSeederDefaultsEnum


class ModelSeederMeta(ABCMeta):
    def __new__(mcs, name, bases, attrs):
        cls = super().__new__(mcs, name, bases, attrs)

        cls._raw_fields = attrs.get("fields") or {}
        cls._excluded_fields = {
            k for k, v in cls._raw_fields.items()
            if v == "exclude" or v == ("exclude",)
        }

        cls.fields = normalize_seeder_fields(cls._raw_fields)

        if cls.fields:
            cls._validate_fields_exist(cls.fields)
            cls._assign_default_fields()

        return cls


class BaseModelSeeder(ABC, metaclass=ModelSeederMeta):
    model_class = None
    fields: dict = None
    default_to = "llm"
    _field_seeders = []

    @classmethod
    def __init__subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        if cls.model_class is None:
            raise ValueError("Seeds must have a model class")

        if cls.fields is None:
            raise ValueError("Seeds must have fields")

        cls._seeders = cls._field_seeders

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
    def seed_data(
            cls,
            count=1,
            fields: dict | None = None
    ) -> list[dict]:
        original_fields = cls.fields.copy()


        if fields:
            cls.fields = {**original_fields, **fields}

        seed_data = []

        for seeder_cls in cls._field_seeders:
            seeder = seeder_cls(cls.fields, cls.default_to)
            seed_data.append(seeder.seed(cls, count))

        formatted_seed_data = [dict() for _ in range(max(len(sublist) for sublist in seed_data))]
        for sublist in seed_data:
            for i, d in enumerate(sublist):
                formatted_seed_data[i].update(d)

        cls.fields = original_fields
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
