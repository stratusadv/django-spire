from __future__ import annotations

from example.cookbook.recipe import models


def update_or_create_recipe_ingredients(
    recipe,
    ingredient_data: list[dict]
) -> list[models.Ingredient]:
    previous_ingredients = (
        recipe
        .ingredients
        .active()
        .values_list('id', flat=True)
    )

    ingredients = []

    for raw_ingredient in ingredient_data:
        ingredient = models.Ingredient(**raw_ingredient)
        ingredient.recipe = recipe
        ingredient.save()
        ingredients.append(ingredient)

    deleted_ids = set(previous_ingredients) - set(
        [ingredient.id for ingredient in ingredients]
    )

    for deleted_ingredient in models.Ingredient.objects.filter(id__in=deleted_ids):
        deleted_ingredient.set_deleted()

    return ingredients
