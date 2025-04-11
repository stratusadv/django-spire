from __future__ import annotations

from typing import Type

from dandy.llm import Prompt
from django.db.models import ForeignKey

from django.db.models.base import Model

from django_spire.seeding.field.callable import CallableFieldSeeder
from django_spire.seeding.field.custom import CustomFieldSeeder
from django_spire.seeding.field.django.seeder import DjangoFieldFakerSeeder, DjangoFieldLlmSeeder
from django_spire.seeding.field.static import StaticFieldSeeder
from django_spire.seeding.model.base import BaseModelSeeder
from django_spire.seeding.model.django.config import DjangoModelFieldsConfig


class DjangoModelSeeder(BaseModelSeeder):
    field_config_class = DjangoModelFieldsConfig

    model_class: Type[Model]
    prompt: Prompt = None
    _field_seeders = [
        CustomFieldSeeder,
        CallableFieldSeeder,
        StaticFieldSeeder,
        DjangoFieldFakerSeeder,
        DjangoFieldLlmSeeder
    ]

    @classmethod
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        if cls.model_class is None:
            raise ValueError("Seeds must have a model class")

        if cls.fields is None:
            raise ValueError("Seeds must have fields")

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
            count = 1,
            fields: dict | None = None
    ) -> list[Model]:
        model_objects = cls.seed(count, fields)
        return cls.model_class.objects.bulk_create(model_objects)
