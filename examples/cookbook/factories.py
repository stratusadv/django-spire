from __future__ import annotations

from typing_extensions import TYPE_CHECKING

if TYPE_CHECKING:
    from examples.cookbook.models import Cookbook, CookbookRecipe


def link_cookbook_recipes(
    cookbook: Cookbook,
    recipe_ids: list[id]
) -> list[CookbookRecipe]:
    previous_recipes = (
        cookbook
        .cookbook_recipes
        .active()
        .values_list('recipe_id', flat=True)
    )

    cookbook_recipes = []

    for recipe_id in set(recipe_ids) - set(previous_recipes):
        cookbook_recipe = cookbook.cookbook_recipes.create(recipe_id=recipe_id)
        cookbook_recipes.append(cookbook_recipe)

    deleted_ids = set(previous_recipes) - set(recipe_ids)

    for delete_cookbook_recipes in cookbook.cookbook_recipes.filter(recipe_id__in=deleted_ids):
        delete_cookbook_recipes.set_deleted()

    return cookbook_recipes
