from __future__ import annotations

from django.db import models
from django.urls import reverse

from django_spire.breadcrumb.models import Breadcrumbs
from django_spire.history.mixins import HistoryModelMixin

from examples.cookbook import querysets


class Cookbook(HistoryModelMixin):
    name = models.CharField(max_length=255)
    description = models.TextField(default='')

    objects = querysets.CookbookQuerySet().as_manager()

    def __str__(self):
        return self.name

    @classmethod
    def base_breadcrumb(cls) -> Breadcrumbs:
        crumbs = Breadcrumbs()
        crumbs.add_breadcrumb('Cookbooks', reverse('cookbook:page:list'))
        return crumbs

    def breadcrumbs(self) -> Breadcrumbs:
        crumbs = Breadcrumbs()
        crumbs.add_base_breadcrumb(self._meta.model)

        if self.pk:
            crumbs.add_breadcrumb(str(self), reverse('cookbook:page:detail', kwargs={'pk': self.pk}))

        return crumbs

    class Meta:
        verbose_name = 'Cookbook'
        verbose_name_plural = 'Cookbooks'
        db_table = 'cookbook'
        permissions = [('can_approve_cookbook', 'Can Approve Cookbook')]


class CookbookRecipe(HistoryModelMixin):
    cookbook = models.ForeignKey(
        'cookbook.Cookbook',
        on_delete=models.CASCADE,
        related_name='cookbook_recipes',
        related_query_name='cookbook_recipe'
    )

    recipe = models.ForeignKey(
        'cookbook_recipe.Recipe',
        on_delete=models.CASCADE,
        related_name='cookbook_recipes',
        related_query_name='cookbook_recipe'
    )

    objects = querysets.CookbookRecipeQuerySet().as_manager()

    def __str__(self):
        return f'Cookbook Recipe {self.pk}'

    class Meta:
        verbose_name = 'Recipe'
        verbose_name_plural = 'Recipes'
        db_table = 'cookbook_recipe_m2m'
