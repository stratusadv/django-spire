from django.db import models
from django.db.models import Choices, QuerySet

from django_spire.contrib.seeding.field.seed.helper.helper import FieldSeedHelper
from django_spire.contrib.seeding.field.seed.model_seed import (
    OrderedForeignKeyModelFieldSeed,
    RandomForeignKeyModelFieldSeed,
)
from django_spire.contrib.seeding.field.seed.ordered_seed import OrderedSequenceFieldSeed
from django_spire.contrib.seeding.field.seed.random_seed import RandomEnumFieldSeed


class ModelFieldSeedHelper(FieldSeedHelper):
    @staticmethod
    def ordered_foreign_key(
        model_class: type[models.Model], wrap: bool = False
    ) -> OrderedForeignKeyModelFieldSeed:
        return OrderedForeignKeyModelFieldSeed(queryset=model_class.objects.all(), wrap=wrap)

    @staticmethod
    def ordered_queryset_foreign_key(
        queryset: QuerySet, wrap: bool = False
    ) -> OrderedForeignKeyModelFieldSeed:
        return OrderedForeignKeyModelFieldSeed(queryset=queryset, wrap=wrap)

    @staticmethod
    def ordered_field_choice(choices: Choices, wrap: bool = False) -> OrderedSequenceFieldSeed:
        return OrderedSequenceFieldSeed(sequence=list(choices), wrap=wrap)

    @staticmethod
    def random_foreign_key(model_class: type[models.Model]) -> RandomForeignKeyModelFieldSeed:
        return RandomForeignKeyModelFieldSeed(queryset=model_class.objects.all())

    @staticmethod
    def random_queryset_foreign_key(queryset: QuerySet) -> RandomForeignKeyModelFieldSeed:
        return RandomForeignKeyModelFieldSeed(queryset=queryset)

    @staticmethod
    def random_field_choice(choices: Choices) -> RandomEnumFieldSeed:
        return RandomEnumFieldSeed(enum_=choices)
