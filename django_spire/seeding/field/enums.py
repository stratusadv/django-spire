from enum import Enum


class FieldSeederTypesEnum(str, Enum):
    LLM = "llm"
    FAKER = "faker"
    STATIC = "static"
    CALLABLE = "callable"
    CUSTOM = "custom"
