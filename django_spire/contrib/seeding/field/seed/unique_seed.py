from __future__ import annotations

import threading
from typing import TYPE_CHECKING, Any, Callable

from django_spire.contrib.seeding.exceptions import DjangoSpireSeederError
from django_spire.contrib.seeding.field.seed.base import BaseFieldSeed

if TYPE_CHECKING:
    from django.db import models


class UniqueFieldSeed(BaseFieldSeed):
    is_cache_unsafe = True

    def __init__(
        self,
        *,
        field_seed: BaseFieldSeed | None = None,
        row_field: str | None = None,
        row_value_callable: Callable[[dict[str, Any]], Any] | None = None,
    ) -> None:
        sources = (field_seed, row_field, row_value_callable)

        if sum(source is not None for source in sources) != 1:
            message = 'Provide exactly one of seed=, row_field=, or row_value_callable='
            raise DjangoSpireSeederError(message)

        self.base_seed = field_seed
        self.base_callable = self._row_field_base(row_field) if row_field is not None else row_value_callable

        self._lock = threading.RLock()
        self._model_class: type[models.Model] | None = None
        self._field_name: str | None = None
        self._max_length: int | None = None
        self._taken: set[Any] | None = None

    @staticmethod
    def _row_field_base(field_name: str) -> Callable[[dict[str, Any]], Any]:
        def base_from_row(row: dict[str, Any]) -> Any:
            return row[field_name]

        return base_from_row

    def generate_cache_key(self) -> str:
        if self.base_seed is not None:
            return f'unique:{self.base_seed.generate_cache_key()}'

        base_key = f'{self.base_callable.__module__}.{self.base_callable.__qualname__}'

        return f'unique:{base_key}'

    def generate_value(self, seed_index: int) -> Any:
        return self.generate_value_context(seed_index)

    def generate_value_context(
        self,
        seed_index: int,
        *,
        model_class: type[models.Model] | None = None,
        field_name: str | None = None,
        row_values: dict[str, Any] | None = None,
    ) -> Any:
        if seed_index == -1:
            self._initialize_run(model_class, field_name)

            return None

        with self._lock:
            self._ensure_run_state()
            base = self._generate_base(seed_index, row_values)
            value = self._unique_value(base)
            self._taken.add(value)

            return value

    def _initialize_run(self, model_class: type[models.Model] | None, field_name: str | None) -> None:
        with self._lock:
            self._model_class = model_class
            self._field_name = field_name
            self._max_length = None
            self._taken = set()

            if model_class is None or field_name is None:
                return

            field = model_class._meta.get_field(field_name)
            self._max_length = getattr(field, 'max_length', None)
            self._taken.update(model_class._default_manager.values_list(field_name, flat=True))

    def _ensure_run_state(self) -> None:
        if self._taken is None:
            self._model_class = None
            self._field_name = None
            self._max_length = None
            self._taken = set()

    def _generate_base(self, seed_index: int, row_values: dict[str, Any] | None) -> Any:
        if self.base_callable is not None:
            return self.base_callable(dict(row_values or {}))

        return self.base_seed.generate_value(seed_index)

    def _unique_value(self, base: Any) -> str:
        value = str(base)
        max_length = self._max_length

        if max_length:
            value = value[:max_length]

        original = value
        suffix = 2

        while value in self._taken:
            value = (
                f'{original[: max_length - len(str(suffix)) - 1]}-{suffix}' if max_length else f'{original}-{suffix}'
            )

            suffix += 1

        return value
