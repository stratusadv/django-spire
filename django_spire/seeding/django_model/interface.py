from typing import Type

from django.db.models.base import Model

from django_spire.seeding.django_model.enums import SeederDefaultToEnum
from django_spire.seeding.interface.interface import BaseSeederFieldInterface


class DjangoModelSeederFieldInterface(BaseSeederFieldInterface):
    # Todo: Need to check that there is a model class here?

    @classmethod
    def _normalize_fields(cls, fields: dict) -> dict:
        fields = super()._normalize_fields(fields)
        cls._validate_fields_exist(fields)
        cls._assign_default_fields()

        return fields

    @classmethod
    def _validate_fields_exist(cls, fields: dict):
        model_fields = {field.name for field in cls.model_class._meta.fields}
        unknown = set(fields.keys()) - model_fields

        if unknown:
            raise ValueError(f"Invalid field name(s): {', '.join(unknown)}")

    @classmethod
    def _assign_default_fields(cls, fields: dict = None):
        if cls.default_to not in SeederDefaultToEnum._value2member_map_:
            raise ValueError(f"Invalid default_to value '{cls.default_to}'. Must be one of: {', '.join([v.value for v in SeederDefaultToEnum])}")

        if cls.default_to == SeederDefaultToEnum.INCLUDED:
            return

        method = cls.default_to.lower()
        default_fields = [
            f.name for f in cls.model_class._meta.fields
            if f.name not in cls.fields or cls.fields.get(f.name) == "exclude"
        ]
        cls.fields.update({field_name: (method,) for field_name in default_fields})

