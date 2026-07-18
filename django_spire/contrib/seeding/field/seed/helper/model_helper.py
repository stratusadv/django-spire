from django.db import models
from django.db.models import Choices, QuerySet

from django_spire.contrib.seeding.field.seed.helper.helper import FieldSeedHelper
from django_spire.contrib.seeding.field.seed.model_seed import OrderedForeignKeyModelFieldSeed, \
    RandomForeignKeyModelFieldSeed
from django_spire.contrib.seeding.field.seed.random_seed import RandomFieldSeed


class ModelFieldSeedHelper(FieldSeedHelper):
    @staticmethod
    def ordered_foreign_key(model_class: type[models.Model]) -> OrderedForeignKeyModelFieldSeed:
        return OrderedForeignKeyModelFieldSeed(queryset=model_class.objects.all())

    @staticmethod
    def ordered_queryset_foreign_key(queryset: QuerySet) -> OrderedForeignKeyModelFieldSeed:
        return OrderedForeignKeyModelFieldSeed(queryset=queryset)

    @staticmethod
    def random_foreign_key(model_class: type[models.Model]) -> RandomForeignKeyModelFieldSeed:
        return RandomForeignKeyModelFieldSeed(queryset=model_class.objects.all())

    @staticmethod
    def random_queryset_foreign_key(queryset: QuerySet) -> RandomForeignKeyModelFieldSeed:
        return RandomForeignKeyModelFieldSeed(queryset=queryset)

    @staticmethod
    def random_field_choice(choices: Choices) -> RandomFieldSeed:
        return RandomFieldSeed(enum_=choices)
