from enum import Enum


class ModelSeederDefaultsEnum(str, Enum):
    LLM = "llm"
    FAKER = "faker"
    INCLUDED = "included"

