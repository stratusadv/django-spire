import random

from django.db import models
from django.db.models import Choices, QuerySet

from django_spire.contrib.seeding.field.seed.callable_seed import CallableFieldSeed
from django_spire.contrib.seeding.field.seed.helper.helper import FieldSeedHelper
from django_spire.contrib.seeding.field.seed.model_seed import OrderedForeignKeyModelFieldSeed
from django_spire.contrib.seeding.field.seed.random_seed import RandomFieldSeed


class ModelFieldSeedHelper(FieldSeedHelper):
    @staticmethod
    def ordered_foreign_key(model_class: type[models.Model]) -> OrderedForeignKeyModelFieldSeed:
        return OrderedForeignKeyModelFieldSeed(queryset=model_class.objects.all())

    @staticmethod
    def ordered_queryset_foreign_key(queryset: QuerySet) -> OrderedForeignKeyModelFieldSeed:
        return OrderedForeignKeyModelFieldSeed(queryset=queryset)

    @staticmethod
    def random_foreign_key(model_class: type[models.Model]) -> CallableFieldSeed:
        return CallableFieldSeed(
            random.choice, seq=list(model_class.objects.all().values_list('id', flat=True))
        )

    @staticmethod
    def random_queryset_foreign_key(queryset: QuerySet) -> CallableFieldSeed:
        return CallableFieldSeed(random.choice, seq=list(queryset.values_list('id', flat=True)))

    @staticmethod
    def random_field_choice(choices: Choices) -> RandomFieldSeed:
        return RandomFieldSeed(enum_=choices)
