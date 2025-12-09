from __future__ import annotations

from enum import Enum


class ModelSeederDefaultsEnum(str, Enum):
    LLM = "llm"
    FAKER = "faker"
    INCLUDED = "included"

