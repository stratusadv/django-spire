from abc import abstractmethod, ABC
from typing import Any

from django_spire.contrib.seeding.field.seed.base import BaseFieldSeed


class BaseMutateFieldSeed(BaseFieldSeed, ABC):
    @abstractmethod
    def __init__(self, field_seed: BaseFieldSeed, *args, **kwargs) -> None:
        self.field_seed = field_seed
        raise NotImplementedError

    def generate_value(self, seed_index: int) -> Any:
        if seed_index == -1:
            return self.field_seed
        else:
            return self._mutate_value(seed_index)

    @abstractmethod
    def _mutate_value(self, seed_index: int) -> Any:
        raise NotImplementedError