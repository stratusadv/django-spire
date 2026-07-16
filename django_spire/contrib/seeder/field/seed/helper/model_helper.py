from typing import Any

from django.db import models
from django.db.models import Choices

from django_spire.contrib.seeder.field.seed.helper.helper import FieldSeedHelper
from django_spire.contrib.seeder.field.seed.model_seed import ModelFieldSeed
from django_spire.contrib.seeder.field.seed.random_seed import RandomFieldSeed


class ModelFieldSeedHelper(FieldSeedHelper):
    @staticmethod
    def random_foreign_key(model_class: type[models.Model]) -> ModelFieldSeed:
        return ModelFieldSeed(model_class=model_class)

    @staticmethod
    def random_field_choice(choices: Choices) -> RandomFieldSeed:
        return RandomFieldSeed(enum_=choices)