from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from django.db import models


class BaseFieldSeed(ABC):
    is_cache_unsafe: bool = False

    @abstractmethod
    def __init__(self, *args, **kwargs) -> None:
        raise NotImplementedError

    @abstractmethod
    def generate_cache_key(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def generate_value(self, seed_index: int) -> Any:
        raise NotImplementedError

    def generate_value_context(
        self,
        seed_index: int,
        *,
        model_class: type[models.Model] | None = None,
        field_name: str | None = None,
        row_values: dict[str, Any] | None = None,
    ) -> Any:
        _ = model_class, field_name, row_values

        return self.generate_value(seed_index)
