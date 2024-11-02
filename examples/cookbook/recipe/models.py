from django.db import models
from django.urls import reverse

from django_spire.breadcrumb.models import Breadcrumbs
from django_spire.history.mixins import HistoryModelMixin

from examples.cookbook.recipe import querysets
from examples.cookbook.recipe.choices import RecipeCourseChoices


class Recipe(HistoryModelMixin):
    name = models.CharField(max_length=255)
    description = models.TextField(default='')

    course = models.CharField(
        max_length=3,
        choices=RecipeCourseChoices.choices,
        default=RecipeCourseChoices.MAIN
    )

    prep_time = models.IntegerField(default=15)
    cook_time = models.IntegerField(default=30)

    servings = models.IntegerField(default=1)

    objects = querysets.RecipeQuerySet.as_manager()

    def __str__(self):
        return self.name

    def breadcrumbs(self):
        crumbs = Breadcrumbs()

        if self.pk:
            crumbs.add_breadcrumb(str(self), reverse('cookbook:recipe:page:detail', kwargs={'pk': self.pk}))

        return crumbs

    def choice_verbose(self):
        return RecipeCourseChoices(self.course).label

    def total_time(self) -> int:
        return self.prep_time + self.cook_time

    def set_deleted(self):
        for cookbook_recipe in self.cookbook_recipes.active():
            cookbook_recipe.set_deleted()

        super().set_deleted()

    class Meta:
        verbose_name = 'Recipe'
        verbose_name_plural = 'Recipes'
        db_table = 'cookbook_recipe'


class Ingredient(HistoryModelMixin):
    recipe = models.ForeignKey(
        'cookbook_recipe.Recipe',
        on_delete=models.CASCADE,
        related_name='ingredients',
        related_query_name='ingredient'
    )

    name = models.CharField(max_length=255)
    quantity = models.CharField(max_length=255, default='')
    directions = models.TextField(default='')

    objects = querysets.IngredientQuerySet.as_manager()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Ingredient'
        verbose_name_plural = 'Ingredients'
        db_table = 'cookbook_ingredient'
