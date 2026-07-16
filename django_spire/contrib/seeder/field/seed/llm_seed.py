from typing import Any

from django_spire.contrib.seeder.field.seed.base import BaseFieldSeed


class LlmFieldSeed(BaseFieldSeed):
    def __init__(self, field_type: type, prompt: str | None = None) -> None:
        self.field_type = field_type
        self.prompt = prompt

    def generate_value(self) -> Any:
        return None
