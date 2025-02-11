from dataclasses import dataclass, field
from typing import Type

from dandy.intel import Intel
from dandy.llm import Prompt
from django.db.models import Model
from pydantic import create_model
from pydantic.fields import FieldInfo

from workspaces.seeding.enums import FIELD_TYPE_TO_TYPE_HINTING
from workspaces.seeding.rules.factories import SeedBotRulePromptFactory


@dataclass
class SeedHelper:
    model_class: Type[Model]

    instructions_prompt: Prompt

    _model_rules_prompt: Prompt = field(default_factory=Prompt)

    count: int = 5

    exclude_fields: list[str] = field(default_factory=list)
    include_fields: list[str] = field(default_factory=list)

    def __post_init__(self):
        self._model_rules_prompt.title('Model Rules:')
        for model_field in self.valid_model_fields:
            rule_prompt = SeedBotRulePromptFactory(model_field).prompt
            self._model_rules_prompt.prompt(rule_prompt)

    @property
    def valid_model_fields(self):
        include = set(self.include_fields)
        exclude = set(self.exclude_fields)

        return [
            f
            for f in self.model_class._meta.fields
            if (not include or f.attname in include) and (f.attname not in exclude)
        ]


    def build_intel_class(self) -> Type[Intel]:
        pydantic_fields = {}

        for model_field in self.valid_model_fields:

            model_field_type = FIELD_TYPE_TO_TYPE_HINTING[model_field.get_internal_type()]

            if model_field.null:
                model_field_type = model_field_type | None
                field_info = FieldInfo(default=None)
            else:
                field_info = FieldInfo()


            pydantic_fields[model_field.attname] = (
                model_field_type,
                field_info
            )

        # intel_class = create_model(
        #     'EmployeeIntel',
        #     __base__=Intel,
        #     **pydantic_fields
        # )

        intel_class = create_model(
            f'{self.model_class.__name__}Intel',
            __base__=Intel,
            **pydantic_fields
        )

        return intel_class


    def bulk_create(self, intel_data: list[Intel]):
        instances = [
            self.model_class(**intel.model_dump())
            for intel in intel_data
        ]

        return self.model_class.objects.bulk_create(instances)
