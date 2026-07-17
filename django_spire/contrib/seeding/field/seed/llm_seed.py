from typing import Any

from django_spire.contrib.seeding.field.seed.base import BaseFieldSeed


class LlmFieldSeed(BaseFieldSeed):
    def __init__(
        self, field_type: type, prompt: str | None = None, locale: str | list[str] = 'en_CA'
    ) -> None:
        self.field_type = field_type
        self.prompt = prompt
        self.locale = locale

    def generate_value(self, seed_index: int) -> Any:
        _ = seed_index

        return None
