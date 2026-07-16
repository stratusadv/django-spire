from typing import Any

from django.db import models

from django_spire.contrib.seeding.field.seed.base import BaseFieldSeed


class ModelFieldSeed(BaseFieldSeed):
    def __init__(self, model_class: type[models.Model]) -> None:
        self.model_class = model_class

    def generate_value(self) -> Any:
        return None
