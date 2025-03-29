from typing import Type

from django.db.models import Model
from dandy.llm import Prompt

from django_spire.seeding.seeding import LlmSeeding, FakerSeeding


class SeedingProcessor:

    def __init__(
            self,
            model_class: Type[Model],
            fields: dict[str, tuple],
            prompt: Prompt = None,
            include_fields: list[str] = None,
            exclude_fields: list[str] = None

    ):
        model_class_fields_names = [field.name for field in model_class._meta.fields]

        # All defined fields must be a valid model field.
        if any(field not in model_class_fields_names for field in fields.keys()):
            raise ValueError(f'Invalid field name(s): {", ".join(fields.keys() - model_class_fields_names)}')

        self.model_class = model_class
        self.prompt = prompt

        self.exclude_fields = exclude_fields or []
        self.include_fields = include_fields or []

    def faker_seed_data(self, count = 1) -> list[dict]:
        return FakerSeeding(
            model_class=self.model_class,
            include_fields=self.include_fields,
            exclude_fields=self.exclude_fields,
            count=count
        ).generate_data()

    def llm_seed_data(self, count = 1) -> list[dict]:
        return LlmSeeding(
            model_class=self.model_class,
            include_fields=self.include_fields,
            exclude_fields=self.exclude_fields,
            count=count
        ).generate_data(prompt=self.prompt)

    def static_seed_data(self, count = 1) -> list[dict]:
        return [{}]

    def callable_seed_data(self, count = 1) -> list[dict]:
        return [{}]

    def seed_data(self, count = 1):
        llm_seed_data = self.llm_seed_data(count)
        faker_seed_data = self.faker_seed_data(count)
        static_seed_data = self.static_seed_data(count)
        callable_seed_data = self.callable_seed_data(count)

        return [
            {**d1, **d2, **d3, **d4}
            for d1, d2, d3, d4 in zip(llm_seed_data, faker_seed_data, static_seed_data, callable_seed_data)
        ]

    def generate_model_objects(self, count = 1):
        return [self.model_class(**seed_data) for seed_data in self.seed_data(count)]

    def seed_database(self):
        model_objects = self.generate_model_objects()
        return self.model_class.objects.bulk_create(model_objects)
