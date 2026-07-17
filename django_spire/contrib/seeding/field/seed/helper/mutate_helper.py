from typing import Callable

from django_spire.contrib.seeding.field.seed.base import BaseFieldSeed
from django_spire.contrib.seeding.field.seed.helper.helper import FieldSeedHelper
from django_spire.contrib.seeding.field.seed.mutate import CorruptMutateFieldSeed
from django_spire.contrib.seeding.field.seed.mutate import MutateSeverity
from django_spire.contrib.seeding.field.seed.mutate import NullableMutateFieldSeed
from django_spire.contrib.seeding.field.seed.mutate import TransformMutateFieldSeed
from django_spire.contrib.seeding.field.seed.mutate import TypeCoercionMutateFieldSeed


class MutateFieldSeedHelper(FieldSeedHelper):
    Severity = MutateSeverity

    @staticmethod
    def corrupt(
        field_seed: BaseFieldSeed,
        corrupt_chance: float = 0.5,
        severity: MutateSeverity = MutateSeverity.MILD,
    ) -> CorruptMutateFieldSeed:
        return CorruptMutateFieldSeed(
            field_seed=field_seed, corrupt_chance=corrupt_chance, severity=severity
        )

    @staticmethod
    def nullable(field_seed: BaseFieldSeed, nullify_chance: float = 0.5) -> NullableMutateFieldSeed:
        return NullableMutateFieldSeed(field_seed=field_seed, nullify_chance=nullify_chance)

    @staticmethod
    def type(
        field_seed: BaseFieldSeed, target_type: type, change_chance: float = 0.5
    ) -> TypeCoercionMutateFieldSeed:
        return TypeCoercionMutateFieldSeed(
            field_seed=field_seed, target_type=target_type, change_chance=change_chance
        )

    @staticmethod
    def value(
        field_seed: BaseFieldSeed, transform: Callable, change_chance: float = 0.5
    ) -> TransformMutateFieldSeed:
        return TransformMutateFieldSeed(
            field_seed=field_seed, transform=transform, change_chance=change_chance
        )
