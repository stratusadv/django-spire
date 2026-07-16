from abc import ABC, abstractmethod
from typing import Any


class BaseFieldSeed(ABC):
    @abstractmethod
    def __init__(self, *args, **kwargs) -> None:
        raise NotImplementedError

    @abstractmethod
    def generate_value(self, **kwargs) -> Any:
        raise NotImplementedError
