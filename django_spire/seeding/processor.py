from dataclasses import dataclass, field
from typing import Type

from dandy.intel import BaseIntel
from dandy.llm import Prompt
from django.db.models import Model
from pydantic import create_model

from django_spire.seeding.maps import MODEL_FIELD_TYPE_TO_TYPE_MAP
from django_spire.seeding.factories import SeedIntelFieldFactory
from django_spire.seeding.intelligence.bots.seeding_bot import SeedingLlmBot


@dataclass
class SeedingProcessor:
    model_class: Type[Model]

    seeding_prompt: Prompt
    
    count: int = 5

    exclude_fields: list[str] = field(default_factory=list)
    include_fields: list[str] = field(default_factory=list)

    @property
    def valid_model_fields(self):
        return [
            f
            for f in self.model_class._meta.fields
            if (not self.include_fields or f.attname in self.include_fields)
               and
               (f.attname not in self.exclude_fields)
        ]

    def build_intel_class(self) -> Type[BaseIntel]:
        pydantic_fields = {}

        for model_field in self.valid_model_fields:

            model_field_type = MODEL_FIELD_TYPE_TO_TYPE_MAP[model_field.get_internal_type()]

            if model_field.null:
                model_field_type = model_field_type | None

            pydantic_fields[model_field.attname] = (
                model_field_type,
                SeedIntelFieldFactory(model_field).build_field()
            )

        seed_intel_class = create_model(
            f'{self.model_class.__name__}Intel',
            __base__=BaseIntel,
            **pydantic_fields
        )

        return seed_intel_class

    def bulk_create(self, seeding_intel_data: list[BaseIntel]):
        instances = [
            self.model_class(**seed_intel.model_dump())
            for seed_intel in seeding_intel_data
        ]

        return self.model_class.objects.bulk_create(instances)

    def seed(self):
        self.bulk_create(
            SeedingLlmBot.process(self)
        )
