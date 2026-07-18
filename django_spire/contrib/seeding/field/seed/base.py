from abc import ABC, abstractmethod

from typing import Any


class BaseFieldSeed(ABC):
    @abstractmethod
    def __init__(self, *args, **kwargs) -> None:
        raise NotImplementedError

    @abstractmethod
    def generate_value(self, seed_index: int) -> Any:
        raise NotImplementedError
