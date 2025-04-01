from enum import Enum


class SeederDefaultToEnum(str, Enum):
    LLM = "llm"
    FAKER = "faker"
    INCLUDED = "included"
