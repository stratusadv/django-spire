from __future__ import annotations

from django.db import models

from django_spire.history.mixins import HistoryModelMixin

from example.cookbook.recipe.nutrition.enums import NutritionFactType
from example.cookbook.recipe.nutrition.querysets import NutritionFactQuerySet


class NutritionFact(HistoryModelMixin):
    recipe = models.ForeignKey(
        'cookbook_recipe.Recipe',
        related_name='nutrition_facts',
        related_query_name='nutrition_fact',
        on_delete=models.CASCADE
    )

    type = models.CharField(max_length=255, choices=NutritionFactType.choices)
    quantity = models.FloatField(default=0)

    objects = NutritionFactQuerySet.as_manager()

    def __str__(self) -> str:
        return self.type

    def type_verbose(self) -> str:
        return NutritionFactType(self.type).label

    class Meta:
        verbose_name = 'Nutrition Fact'
        verbose_name_plural = 'Nutrition Facts'
        db_table = 'recipe_nutrition_fact'
