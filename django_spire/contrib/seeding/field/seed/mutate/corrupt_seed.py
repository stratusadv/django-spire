import random
from typing import Any

from django_spire.contrib.seeding.field.seed.base import BaseFieldSeed
from django_spire.contrib.seeding.field.seed.mutate.base import BaseMutateFieldSeed
from django_spire.contrib.seeding.field.seed.mutate.choices import MutateSeverity

from django_spire.contrib.seeding.field.seed.mutate.corrupt import datetime
from django_spire.contrib.seeding.field.seed.mutate.corrupt import number
from django_spire.contrib.seeding.field.seed.mutate.corrupt import string
from django_spire.contrib.seeding.field.seed.mutate.corrupt import type_swap


class CorruptMutateFieldSeed(BaseMutateFieldSeed):
    def __init__(
        self, field_seed: BaseFieldSeed, corrupt_chance: float, severity: MutateSeverity
    ) -> None:
        self.field_seed = field_seed
        self.corrupt_chance = corrupt_chance
        self.severity = severity

    def _mutate_value(self, seed_index: int) -> Any:
        value = self.field_seed.generate_value(seed_index=seed_index)

        if random.random() >= self.corrupt_chance:
            return value

        if value is None:
            return value

        return self._corrupt_by_severity(value, self.severity)

    def _corrupt_by_severity(self, value: Any, severity: MutateSeverity | None) -> Any:
        severity_str = severity.value if severity else 'mild'
        is_chaos = severity == MutateSeverity.CHAOS
        methods = self._collect_methods_for_value(value, severity_str, is_chaos)
        if not methods:
            return str(value)
        func = random.choice(list(methods.values()))
        return func(value)

    def _collect_methods_for_value(
        self, value: Any, severity: str, is_chaos: bool
    ) -> dict[str, Any]:
        if is_chaos:
            return self._collect_methods(severity)
        if isinstance(value, str):
            return string.get_methods(severity)
        if isinstance(value, (int, float)):
            return number.get_methods(severity)
        if hasattr(value, 'year') and hasattr(value, 'hour'):
            return datetime.get_methods(severity)
        if hasattr(value, 'year'):
            return datetime.get_methods(severity)
        return {}

    def _collect_methods(self, severity: str) -> dict[str, Any]:
        all_methods: dict[str, Any] = {}
        for module in [string, number, type_swap, datetime]:
            all_methods.update(module.get_methods(severity))
        return all_methods
