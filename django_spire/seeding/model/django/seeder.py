from __future__ import annotations

from typing import Type

from dandy.llm import Prompt

from django.db.models.base import Model

from django_spire.seeding.field import (
    CallableFieldSeeder,
    CustomFieldSeeder,
    StaticFieldSeeder
)

from django_spire.seeding.field.django.seeder import DjangoFieldFakerSeeder, DjangoFieldLlmSeeder
from django_spire.seeding.model.base import BaseModelSeeder


class DjangoModelSeeder(BaseModelSeeder):
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
    def field_names(cls) -> list[str]:
        return [field.name for field in cls.model_class._meta.fields]

    @classmethod
    def seed_database(
            cls,
            count = 1,
            fields: dict | None = None
    ) -> list[Model]:
        model_objects = cls.seed(count, fields)
        return cls.model_class.objects.bulk_create(model_objects)
