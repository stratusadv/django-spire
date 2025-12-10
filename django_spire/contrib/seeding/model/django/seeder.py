from __future__ import annotations

from typing import TypeVar, TYPE_CHECKING

from django.db.models.base import Model
from django.db.models import ForeignKey

from django_spire.contrib.seeding.field.callable import CallableFieldSeeder
from django_spire.contrib.seeding.field.custom import CustomFieldSeeder
from django_spire.contrib.seeding.field.django.seeder import DjangoFieldFakerSeeder, DjangoFieldLlmSeeder
from django_spire.contrib.seeding.field.static import StaticFieldSeeder
from django_spire.contrib.seeding.model.base import BaseModelSeeder
from django_spire.contrib.seeding.model.django.config import DjangoModelFieldsConfig

if TYPE_CHECKING:
    from dandy import Prompt


TypeModel = TypeVar('TypeModel', bound=Model)


class DjangoModelSeeder(BaseModelSeeder):
    field_config_class = DjangoModelFieldsConfig

    model_class: type[Model]
    prompt: Prompt = None
    _field_seeders = [
        CustomFieldSeeder,
        CallableFieldSeeder,
        StaticFieldSeeder,
        DjangoFieldFakerSeeder,
        DjangoFieldLlmSeeder
    ]

    @classmethod
    def __init_subclass__(cls, **kwargs) -> None:
        super().__init_subclass__(**kwargs)

        if cls.model_class is None:
            message = "Seeds must have a model class"
            raise ValueError(message)

        if cls.fields is None:
            message = "Seeds must have fields"
            raise ValueError(message)

    @classmethod
    def field_names(cls) -> list[str]:
        # All foreign keys must be _id
        return [
            f.attname if isinstance(f, ForeignKey) else f.name
            for f in cls.model_class._meta.fields
        ]

    @classmethod
    def seed_database(
        cls,
        count: int = 1,
        fields: dict | None = None
    ) -> list[TypeModel]:
        model_objects = cls.seed(count, fields)
        return cls.model_class.objects.bulk_create(model_objects)
